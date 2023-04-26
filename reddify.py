"""Reddify.

Send a push notification when a keyword is mentioned in a selected set of subreddits.
"""

import logging
import multiprocessing
import pathlib
import time

import praw
import pushover_complete
import toml


def is_subscribed_keyword(x: praw.models.Submission, keywords: dict) -> bool:
    """Check if a submission title contains a keyword."""
    if not x:
        return False
    logging.debug("Looking for subscribed keywords in %s", x.subreddit.display_name)
    for keyword in keywords[x.subreddit.display_name]:
        for attr in ["title", "selftext", "body"]:
            if hasattr(x, attr) and keyword.lower() in getattr(x, attr).lower():
                return True
    return False


def reddify(
    reddit: praw.Reddit,
    push: pushover_complete.PushoverAPI,
    user_id: str,
    keywords: dict,
    kind: str,
) -> bool:
    """Stream submissions or comments and send a notification when a keyword is used."""
    if not keywords:
        logging.info("No streams setup for %s.", kind)
        return True
    logging.info("Starting a %s stream for %s subreddits.", kind, len(keywords))
    for content in getattr(reddit.subreddit("+".join(keywords)).stream, kind)():
        if content is None:
            break
        if is_subscribed_keyword(content, keywords):
            if kind == "submissions":
                logging.info("%s - %s", kind, content.title)
                res = push.send_message(
                    user=user_id,
                    title=f"{content.subreddit.display_name}: {content.title}",
                    url=content.permalink,
                    message=content.selftext,
                )
            else:
                logging.info("%s", kind)
                res = push.send_message(
                    user=user_id,
                    title=f"{content.subreddit.display_name}: {content.permalink}",
                    url=content.permalink,
                    message=content.body,
                )

            # Pushover may ban your IP if you send repeated failed requests.
            # On the off-chance that something is wrong, we'll wait for a while.
            if res["status"] != 1:
                logging.error("Pushover returned status %s", res.status)
                time.sleep(1800)
    return True


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %X %p",
    )

    for path in [
        pathlib.Path("reddify.toml"),
        pathlib.Path().home().joinpath(".config/reddify.toml"),
        pathlib.Path().home().joinpath("reddify.toml"),
    ]:
        if path.exists():
            logging.info("Found config in %s", path)
            config = toml.load(path)
            PUSHOVER = config.get("pushover")
            REDDIT = config.get("reddit")
            SUBMISSIONS = config.get("submissions")
            COMMENTS = config.get("comments")

        reddit = praw.Reddit(
            client_id=REDDIT.get("CLIENT_ID"),
            client_secret=REDDIT.get("CLIENT_SECRET"),
            user_agent=REDDIT.get("USER_AGENT"),
        )

        push = pushover_complete.PushoverAPI(PUSHOVER.get("API_KEY"))
    with multiprocessing.Pool(2) as pool:
        submissions = pool.apply_async(
            reddify,
            kwds={
                "reddit": reddit,
                "push": push,
                "user_id": PUSHOVER.get("USER_ID"),
                "keywords": SUBMISSIONS,
                "kind": "submissions",
            },
        )
        comments = pool.apply_async(
            reddify,
            kwds={
                "reddit": reddit,
                "push": push,
                "user_id": PUSHOVER.get("USER_ID"),
                "keywords": COMMENTS,
                "kind": "comments",
            },
        )
        pool.close()
        pool.join()
