import instaloader
from instaloader.exceptions import ProfileNotExistsException, ConnectionException, LoginRequiredException

# Create an Instaloader object
loader = instaloader.Instaloader()

try:
    # Take the Instagram username as input from the user
    username = input("Enter Instagram username: ").strip()

    # Fetch the profile details using the Instaloader object
    profile = instaloader.Profile.from_username(loader.context, username)

    # Print profile details
    print(f"Username: {profile.username}")
    print(f"Number of Posts Uploaded: {profile.mediacount}")
    print(f"{profile.username} has {profile.followers} followers.")
    print(f"{profile.username} is following {profile.followees} people.")
    print(f"Bio: {profile.biography or 'No bio available'}")

    # Download the profile picture only
    loader.download_profile(username, profile_pic_only=True)
    print(f"Profile picture downloaded for {username}")

except ProfileNotExistsException:
    print(f"Error: The username '{username}' does not exist.")
except ConnectionException:
    print("Error: Failed to connect to Instagram. Check your internet connection.")
except LoginRequiredException:
    print("Error: This action requires logging in. Please configure Instaloader with your credentials.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")