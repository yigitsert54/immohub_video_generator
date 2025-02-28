from connector import Connector
from video_generator import VideoGenerator
from openai import OpenAI
from keys import OPEN_AI_KEY
import traceback


def extract_immo_data(data):
    return {
        'description_text': data["description_text"],
        'price-text': data["price_text"],
        'price': data["price"],
        'location': data["location"],
        'rentorbuy': data["rentorbuy"],
        'flatorhouse': data["flatorhouse"],
        'squarefeets': data["squarefeets"],
        'images': data["images"],
        'logo_url': data["logo_url"]
    }


def generate_video(generator, selected_template, prop_id, prop_data, colors, settings):

    video = None

    if selected_template == "template_1":
        video = generator.render_template_v1(prop_id, prop_data, colors, settings)
    elif selected_template == "template_2":
        video = generator.render_template_v2(prop_id, prop_data, colors, settings)
    elif selected_template == "template_3":
        video = generator.render_template_v3(prop_id, prop_data, colors, settings)
    elif selected_template == "template_4":
        video = generator.render_template_v4(prop_id, prop_data, colors, settings)
    elif selected_template == "template_5":
        video = generator.render_template_v5(prop_id, prop_data, colors, settings)

    return video


# initialize Connector
connector = Connector()

# initialize Open AI Client
client = OpenAI(api_key=OPEN_AI_KEY)

# initialize Video Generator
video_generator = VideoGenerator(client=client)

# Delete image directories
video_generator.delete_directories()

# Get video data for new or updated properties
video_data_list = connector.get_video_data()

print("\n#####################################################################################")
print("STARTING VIDEO GENERATION")
print("#####################################################################################\n")

# Loop though each property to extract necessary data
for i, video_data in enumerate(video_data_list):

    print(f" - Generating video {i + 1} of {len(video_data_list)} entries in video_data_list...\n")

    # Extract account id in immohub server
    immohub_account_id = video_data["immohub_account_id"]

    # Extract property id
    property_id = video_data["property_id"]

    # Extract immo data
    immo_data = extract_immo_data(video_data["immo_data"])

    # Extract color_data
    color_data = video_data["color_data"]

    # Extra further settings
    further_settings = video_data["further_settings"]

    # Loop through missing video count
    for counter in range(further_settings["number_of_videos"]):

        # Generate video
        try:
            video_name = generate_video(
                generator=video_generator,
                selected_template=video_data["selected_template"],
                prop_id=property_id,
                prop_data=immo_data,
                colors=color_data,
                settings=further_settings
            )
        except Exception as e:
            print(f"Error Generating video in {__file__}: {e}")
            traceback.print_exc()
        else:
            if video_name is not None:
                print("Video Creation Successful...")
                connector.save_video_in_server(property_id, video_name)

        print("\n-------------------------------------------------------------------------------\n")

# Delete image directories
video_generator.delete_directories()