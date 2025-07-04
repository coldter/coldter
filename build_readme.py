import praw  # New import
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()

# --- Reddit API Credentials from Environment Variables ---
# Make sure you have set these in your environment!
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT",default="ReadmeUpdater v1.0")


def get_top_reddit_image(subreddit_name, time_filter="day", limit=25):
    """
    Fetches the top-voted image post from a subreddit and returns it as an HTML snippet.

    Args:
        subreddit_name (str): The name of the subreddit.
        time_filter (str): Time period to consider ('all', 'year', 'month', 'day').
        limit (int): How many top posts to check.

    Returns:
        str: An HTML <a> tag with the image, or a fallback message on failure.
    """
    if not all([CLIENT_ID, CLIENT_SECRET, USER_AGENT]):
        print("Error: Reddit API environment variables are not set.")
        return "<a><p>Error: Reddit API credentials not configured.</p></a>"

    try:
        print("Connecting to Reddit...")
        reddit = praw.Reddit(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT
        )
        reddit.read_only = True  # We only need to read data

        print(f"Fetching top posts from r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)

        for post in subreddit.top(time_filter=time_filter, limit=limit):
            # Check for a direct link to a common static image format
            # Excludes text posts, videos, and gifs
            if not post.is_self and post.url.lower().endswith(
                (".png", ".jpg", ".jpeg")
            ):
                print(f"Found image post: {post.title}")
                # Construct the full URL to the post comments
                post_url = f"https://www.reddit.com{post.permalink}"
                # Return the HTML chunk in the desired format
                return f'<a href="{post_url}"><img max-height="400" width="350" src="{post.url}"></a>'

        print(f"No suitable image posts found in the top {limit} posts.")
        # Fallback if no image is found in the top posts
        return '<a href="https://www.reddit.com/r/ProgrammerHumor/"><p>Could not fetch a top image. Click to visit the subreddit.</p></a>'

    except Exception as e:
        print(f"An error occurred while fetching from Reddit: {e}")
        return f"<a><p>An error occurred: {e}</p></a>"


def replace_chunk(content, marker, chunk, inline=False):
    """
    Finds a marked chunk in content and replaces it.
    This function is unchanged from your original code.
    """
    r = re.compile(
        r"<!-- {} starts -->.*<!-- {} ends -->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def yearProgress():
    """
    This function is unchanged from your original code.
    """
    txt_yearProgress = root / "yearProgress.txt"
    txt_pro = txt_yearProgress.open(encoding="utf-8").read()
    return txt_pro


if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open(encoding="utf-8").read()
    rewritten = readme_contents

    # Use the new function to get the image from Reddit
    programmer_humor_chunk = get_top_reddit_image("programmerhumor")
    rewritten = replace_chunk(rewritten, "programmer_humor_img", programmer_humor_chunk)

    # This part remains the same
    rewritten = replace_chunk(rewritten, "yearProgress", yearProgress())

    readme.open("w", encoding="utf-8").write(rewritten)
    print("README.md has been updated successfully.")
