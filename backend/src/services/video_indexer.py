import os
import time
import json
import logging
import subprocess
import requests
import yt_dlp

logger = logging.getLogger("video-indexer")


class VideoIndexerService:
    def __init__(self):
        self.account_id = os.getenv("AZURE_VI_ACCOUNT_ID")
        self.location = os.getenv("AZURE_VI_LOCATION")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.vi_name = os.getenv("AZURE_VI_NAME", "project-brand-guardian-001")

        required_env_vars = {
            "AZURE_VI_ACCOUNT_ID": self.account_id,
            "AZURE_VI_LOCATION": self.location,
            "AZURE_SUBSCRIPTION_ID": self.subscription_id,
            "AZURE_RESOURCE_GROUP": self.resource_group,
            "AZURE_VI_NAME": self.vi_name,
        }

        missing = [key for key, value in required_env_vars.items() if not value]
        if missing:
            raise ValueError(
                f"Missing required environment variables for Video Indexer: {', '.join(missing)}"
            )

        self.az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
        if not os.path.exists(self.az_cmd):
            raise FileNotFoundError(
                f"Azure CLI not found at expected path: {self.az_cmd}"
            )

    def get_access_token(self):
        """Gets an ARM access token by directly invoking Azure CLI."""
        try:
            cmd = [
                self.az_cmd,
                "account",
                "get-access-token",
                "--resource",
                "https://management.azure.com/",
                "--output",
                "json",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                shell=False,
            )

            token_data = json.loads(result.stdout)
            access_token = token_data.get("accessToken")

            if not access_token:
                raise Exception(
                    f"Azure CLI returned no accessToken. Raw output: {result.stdout}"
                )

            return access_token

        except subprocess.CalledProcessError as e:
            logger.error(f"Azure CLI command failed. stderr: {e.stderr}")
            raise Exception(f"Failed to get Azure token via Azure CLI: {e.stderr}") from e
        except Exception as e:
            logger.error(f"Failed to get Azure Token: {e}")
            raise

    def get_account_token(self, arm_access_token):
        """Exchanges ARM token for Video Indexer account token."""
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.vi_name}"
            f"/generateAccessToken?api-version=2024-01-01"
        )
        headers = {"Authorization": f"Bearer {arm_access_token}"}
        payload = {"permissionType": "Contributor", "scope": "Account"}

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to get VI Account Token: {response.text}")

        return response.json().get("accessToken")

    def download_youtube_video(self, url, output_path="temp_video.mp4"):
        """Downloads a YouTube video to a local file."""
        logger.info(f"Downloading YouTube video: {url}")

        ydl_opts = {
            "format": "best",
            "outtmpl": output_path,
            "quiet": False,
            "no_warnings": False,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"]
                }
            },
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36"
                )
            },
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logger.info("Download complete.")
            return output_path
        except Exception as e:
            raise Exception(f"YouTube Download Failed: {str(e)}")

    def upload_video(self, video_path, video_name):
        """Uploads a local file to Azure Video Indexer."""
        arm_token = self.get_access_token()
        vi_token = self.get_account_token(arm_token)

        api_url = (
            f"https://api.videoindexer.ai/{self.location}/Accounts/"
            f"{self.account_id}/Videos"
        )

        params = {
            "accessToken": vi_token,
            "name": video_name,
            "privacy": "Private",
            "indexingPreset": "Default",
        }

        logger.info(f"Uploading file {video_path} to Azure...")

        with open(video_path, "rb") as video_file:
            files = {"file": video_file}
            response = requests.post(api_url, params=params, files=files)

        if response.status_code != 200:
            raise Exception(f"Azure Upload Failed: {response.text}")

        response_json = response.json()
        logger.info(f"Azure upload response: {response_json}")
        return response_json.get("id")

    def wait_for_processing(self, video_id, max_wait_minutes=15, poll_interval_seconds=30):
        """Polls video indexing status until complete or timeout."""
        logger.info(f"Waiting for video {video_id} to process...")

        arm_token = self.get_access_token()
        vi_token = self.get_account_token(arm_token)

        url = (
            f"https://api.videoindexer.ai/{self.location}/Accounts/"
            f"{self.account_id}/Videos/{video_id}/Index"
        )

        start_time = time.time()
        attempt = 1

        while True:
            elapsed_seconds = time.time() - start_time
            elapsed_minutes = elapsed_seconds / 60

            if elapsed_minutes >= max_wait_minutes:
                raise TimeoutError(
                    f"Video Indexer processing timed out after {max_wait_minutes} minutes "
                    f"for video_id={video_id}"
                )

            params = {"accessToken": vi_token}
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            state = data.get("state")

            logger.info(
                f"Polling attempt {attempt} | state={state} | elapsed={elapsed_minutes:.1f} min"
            )

            if state == "Processed":
                logger.info("Video processing completed successfully.")
                return data
            if state == "Failed":
                raise Exception(f"Video Indexing Failed in Azure. Response: {data}")
            if state == "Quarantined":
                raise Exception(
                    f"Video Quarantined (Copyright/Content Policy Violation). Response: {data}"
                )

            time.sleep(poll_interval_seconds)
            attempt += 1

    def extract_data(self, vi_json):
        """Parses the Azure Video Indexer JSON into the pipeline state format."""
        transcript_lines = []
        for v in vi_json.get("videos", []):
            for insight in v.get("insights", {}).get("transcript", []):
                text = insight.get("text")
                if text:
                    transcript_lines.append(text)

        ocr_lines = []
        for v in vi_json.get("videos", []):
            for insight in v.get("insights", {}).get("ocr", []):
                text = insight.get("text")
                if text:
                    ocr_lines.append(text)

        return {
            "transcript": " ".join(transcript_lines),
            "ocr_text": ocr_lines,
            "video_metadata": {
                "duration": vi_json.get("summarizedInsights", {})
                .get("duration", {})
                .get("seconds"),
                "platform": "youtube",
            },
        }