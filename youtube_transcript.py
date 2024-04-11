# pip install langchain-community
# pip install --upgrade youtube-transcript-api
# pip install pytube
from langchain_community.document_loaders import YoutubeLoader

# https://python.langchain.com/docs/integrations/document_loaders/youtube_transcript
# 
# works for both YouTube videos and lives:
#   "https://youtu.be/0wPZcZGY7YQ?si=XNVjn1nS8OWLKGBk", 
#   "https://www.youtube.com/live/svuektNW7dk?si=mPCXNYaXVUe1KPH9",
# 	"https://www.youtube.com/live/oCq5QCbsdQ8?si=15_3-K1yfHew4q8K",
# 	"https://www.youtube.com/live/Seu8KkqBY1k?si=cGrmdVArmk82UDOC",
#   "https://www.youtube.com/live/oCq5QCbsdQ8?si=SrsfqE5Y31uE3x-o",


loader = YoutubeLoader.from_youtube_url(
	"https://www.youtube.com/live/-oPYGeAdgFI?si=_zj1PNkbjSExICQQ",
	add_video_info=True,
	language=["en", "es"],
	translation="en",
)

docs = loader.load()

if len(docs) > 0:
    print(docs[0].page_content)
    print("Length of docs:", len(docs[0].page_content))
else:
    print("docs is empty")
