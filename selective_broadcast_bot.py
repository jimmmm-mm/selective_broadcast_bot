import numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns, warnings
from instagram_private_api import Client

warnings.filterwarnings("ignore")
plt.style.use("ggplot")


class selective_broadcast_bot(object):
    def __init__(self, login_username, login_password):
        api = Client(login_username, login_password)
        self.api = api
        self.user_id = self.api.authenticated_user_id
        self.rank_token = self.api.generate_uuid()

    def get_currently_followers(self, generate_csv=True):
        results = self.api.user_followers(
            user_id, rank_token=rank_token, count=200, extract=False
        )
        followers_username = list(map(lambda x: x["username"], results["users"]))
        followers_user_id = list(map(lambda x: x["pk"], results["users"]))
        print(f"you have currently {len(followers_username)} followers")
        df = pd.DataFrame(followers_username, columns=["user_name"])
        ddf = pd.DataFrame([followers_username, followers_user_id]).T
        ddf.columns = ["user_name", "user_id"]
        df = pd.merge(df, ddf, on=["user_name"], how="left")
        df["class"] = ""
        if generate_csv:
            df.to_csv("followers.csv", index=False, encoding="utf-8-sig")
        else:
            self.df = df

    def piechart_for_current_class(self, df):
        self.labeled_df = df
        df["class"].value_counts().plot.pie(figsize=(8, 8), autopct="%1.1f%%")
        plt.title("Friends class")
        plt.legend()

    def _get_currently_block_users(self):
        blocked_dict = self.api.blocked_reels()
        blocked_username = list(map(lambda x: x["username"], blocked_dict["users"]))
        blocked_user_id = list(map(lambda x: x["pk"], blocked_dict["users"]))
        return blocked_user_id, blocked_username

    def select_block_users(self, by: str, _list: list):
        assert by in self.labeled_df.columns, "Find no reference"
        wanna_block_df = self.labeled_df[self.labeled_df[by].isin(_list)]
        (
            already_blocked_user_id,
            already_blocked_username,
        ) = self._get_currently_block_users()

        # user_id
        cancel_block_list = list(
            set(already_blocked_user_id).difference(set(wanna_block_df["user_id"]))
        )
        # user_id
        add_in_block_list = list(
            set(wanna_block_df["user_id"]).difference(set(already_blocked_user_id))
        )

        # cancel block
        self._cancel_block(cancel_block_list)
        # block them
        self._block_them(add_in_block_list)

        print("process completed")

    def _cancel_block(self, cancel_block_list: list):
        result = set(
            map(
                lambda x: self.api.set_reel_block_status(x, block_status="unblock")[
                    "status"
                ],
                cancel_block_list,
            )
        )
        if result in [set("ok"), set()]:
            print("block complete")
        else:
            print("error occurred during blocking")

    def _block_them(self, block_list: list):
        result = set(map(lambda x: self.api.block_friend_reel(x)["status"], block_list))
        if result in [set("ok"), set()]:
            print("block complete")
        else:
            print("error occurred during blocking")


if __name__ == "__main__":
    with open("login_info.secret", mode="r+") as f:
        info = f.read().splitlines()
    info = {k.split(":")[0]: k.split(":")[1] for k in info}

    bot = selective_broadcast_bot(**info)
    bot.get_currently_followers(generate_csv=True)
    while True:
        inp = input("type ok if you already manually created your label")
        if inp.upper() == "ok".upper():
            break

    df = pd.read_csv("followers.csv")
    bot.piechart_for_current_class(df=df)
    bot.select_block_users(by="class", _list=["net", "cousin"])
