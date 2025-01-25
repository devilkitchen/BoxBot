import requests
import aria2p
from datetime import datetime
import asyncio
import os
import time
import logging
from status import format_progress_bar  # Ensure this module is correctly implemented

# Initialize aria2
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""  # Add secret if your aria2 instance requires it
    )
)

async def download_video(url, reply_msg, user_mention, user_id):
    try:
        # Fetch download details
        response = requests.get(f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={url}")
        response.raise_for_status()
        data = response.json()

        # Validate response structure
        if "response" not in data or not data["response"]:
            raise Exception("Invalid response from the server")

        resolutions = data["response"][0].get("resolutions")
        if not resolutions or "Fast Download" not in resolutions:
            raise Exception("Fast Download link not available")

        fast_download_link = resolutions["Fast Download"]
        thumbnail_url = data["response"][0].get("thumbnail", "")
        video_title = data["response"][0].get("title", "Unknown Title")

        # Add download URI to aria2
        download = aria2.add_uris([fast_download_link])
        start_time = datetime.now()

        while download.status != "complete":
            download.update()
            percentage = download.progress
            done = download.completed_length
            total_size = download.total_length
            speed = download.download_speed
            eta = download.eta
            elapsed_time_seconds = (datetime.now() - start_time).total_seconds()

            progress_text = format_progress_bar(
                filename=video_title,
                percentage=percentage,
                done=done,
                total_size=total_size,
                status="Downloading",
                eta=eta,
                speed=speed,
                elapsed=elapsed_time_seconds,
                user_mention=user_mention,
                user_id=user_id,
                aria2p_gid=download.gid
            )

            try:
                await reply_msg.edit_text(progress_text)
            except Exception as e:
                logging.warning(f"Error updating progress message: {e}")
            await asyncio.sleep(2)

        if download.status == "complete":
            file_path = download.files[0].path

            # Download thumbnail
            thumbnail_path = "https://envs.sh/fiW.jpg"
            if thumbnail_url:
                thumbnail_response = requests.get(thumbnail_url)
                with open(thumbnail_path, "wb") as thumb_file:
                    thumb_file.write(thumbnail_response.content)

            await reply_msg.edit_text("ᴜᴘʟᴏᴀᴅɪɴɢ...")

            return file_path, thumbnail_path, video_title
        else:
            raise Exception("Download failed")

    except Exception as e:
        logging.error(f"Error in download_video: {e}")
        await reply_msg.edit_text(f"Error: {e}")
        raise

async def upload_video(client, file_path, thumbnail_path, video_title, reply_msg, collection_channel_id, user_mention, user_id, message):
    try:
        file_size = os.path.getsize(file_path)
        uploaded = 0
        start_time = datetime.now()
        last_update_time = time.time()

        async def progress(current, total):
            nonlocal uploaded, last_update_time
            uploaded = current
            percentage = (current / total) * 100
            elapsed_time_seconds = (datetime.now() - start_time).total_seconds()

            if time.time() - last_update_time > 2:
                progress_text = format_progress_bar(
                    filename=video_title,
                    percentage=percentage,
                    done=current,
                    total_size=total,
                    status="Uploading",
                    eta=(total - current) / (current / elapsed_time_seconds) if current > 0 else 0,
                    speed=current / elapsed_time_seconds if current > 0 else 0,
                    elapsed=elapsed_time_seconds,
                    user_mention=user_mention,
                    user_id=user_id,
                    aria2p_gid=""
                )
                try:
                    await reply_msg.edit_text(progress_text)
                    last_update_time = time.time()
                except Exception as e:
                    logging.warning(f"Error updating progress message: {e}")

        # Upload the video
        with open(file_path, 'rb') as file:
            collection_message = await client.send_video(
                chat_id=collection_channel_id,
                video=file,
                caption=f"✨ {video_title}\n👤 ʟᴇᴇᴄʜᴇᴅ ʙʏ : {user_mention}\n📥 ᴜsᴇʀ ʟɪɴᴋ: tg://user?id={user_id}",
                thumb=thumbnail_path,
                progress=progress
            )
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=collection_channel_id,
                message_id=collection_message.id
            )
            await asyncio.sleep(1)
            await message.delete()
            await message.reply_sticker("CAACAgIAAxkBAAEZdwRmJhCNfFRnXwR_lVKU1L9F3qzbtAAC4gUAAj-VzApzZV-v3phk4DQE")

        await reply_msg.delete()

        # Clean up files
        os.remove(file_path)
        os.remove(thumbnail_path)
        return collection_message.id

    except Exception as e:
        logging.error(f"Error in upload_video: {e}")
        await reply_msg.edit_text(f"Error: {e}")
        raise
