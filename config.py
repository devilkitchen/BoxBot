import os

#Database 
#Database
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://cristi7jjr:tRjSVaoSNQfeZ0Ik@cluster0.kowid.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "Terabox")

#Shortner (token system) 
# check my discription to help by using my refer link of shareus.io


SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "shrinkme.io")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "317e5f6ab1aa6fba5fb3623a24caf6a26f6e177e")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 43200)) # Add time in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "True")
TUT_VID = os.environ.get("TUT_VID", "https://t.me/HowToDownloadMoviePrime/5") # shareus ka tut_vid he
