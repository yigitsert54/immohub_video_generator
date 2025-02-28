import requests
from urls import ROOT_DOMAIN


class Connector:

    def __init__(self):
        pass

    @staticmethod
    def get_video_data():

        # Endpoint to get property data of all properties needing a video
        data_endpoint = ROOT_DOMAIN + "immohub/get-video-data/"

        # Execute request
        r = requests.get(data_endpoint)

        if r.status_code == 200:

            try:
                response = r.json()
            except requests.exceptions.JSONDecodeError:
                print("Error! - JSONDecodeError - No json received!")
                return []
            else:
                return response

        else:
            print("Error! - Statuscode:", r.status_code)
            return []

    @staticmethod
    def save_video_in_server(property_id, video_name):

        # endpoint
        endpoint = ROOT_DOMAIN + "immohub/create-video-object/"

        # Create post data
        post_data = {
            "video_name": f'{video_name}.mp4',
            "property_id": property_id
        }

        # execute post request
        r = requests.post(endpoint, json=post_data)

        if r.status_code == 200:
            print(f"\nVideo sent to server! -> '{video_name}.mp4'")


if __name__ == "__main__":

    connector = Connector()
    video_data_list = connector.get_video_data()

    prop_id = "f3218c66-d784-4b3d-86a6-3d074ae3caf5"
    v_name = "f34598c66-d784-4b3d-86a6-3d07543caf5"

    connector.save_video_in_server(prop_id, v_name)
