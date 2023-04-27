import asyncio
from collections import defaultdict
from typing import Awaitable, Optional
from nonebot import on_message, on_request, get_bot, logger, get_driver
from nonebot.typing import T_State
from nonebot.rule import keyword, to_me, Rule
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GroupRequestEvent
from nonebot.adapters.onebot.v11 import MessageSegment, Message, permission, GroupMessageEvent
from nonebot.permission import Permission
from src.common.config import BotConfig, GroupConfig
import random
import time
import os
import re

duel_player1 = defaultdict(list)
role_cache = defaultdict(lambda : defaultdict(str))


async def am_I_admin(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    info = await get_bot(str(event.self_id)).call_api('get_group_member_info', **{
        'user_id': event.self_id,
        'group_id': event.group_id
    })
    role = info['role']
    role_cache[event.self_id][event.group_id] = role
    return role == 'admin' or role == 'owner'

async def am_at_admin(bot: Bot, event: GroupMessageEvent, state: T_State, duel_player: list) -> bool:
    info = await get_bot(str(event.self_id)).call_api('get_group_member_info', **{
        'user_id': duel_player[0],
        'group_id': event.group_id
    })
    role = info['role']
    role_cache[event.self_id][event.group_id] = role
    return role == 'admin' or role == 'owner'

async def is_duel_msg(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    curr_event = event.get_plaintext().strip()
    if curr_event in ['牛牛决斗']:
        return True
    return False


duel_msg = on_message(
    priority=3,
    block=True,
    rule=Rule(is_duel_msg),
    permission=permission.GROUP
)


async def duel(messagae_handle, bot: Bot, event: GroupMessageEvent, state: T_State):
    str_temp = event.self_id
    raw_message = event.raw_message
    pattern = re.compile(r"\[CQ:at,qq=(\d+)\]")
    duel_player2 = pattern.findall(raw_message)
    if len(duel_player2) == 0:
        await messagae_handle.send("牛牛不可以这样使用...请输入\"牛牛决斗@决斗者\"来开启功能！")
    elif len(duel_player2) >= 2:
        await messagae_handle.send("不可以...那里...那里不可以进来这么多，一个就好...一个。")
    else:
        match = re.search(r'user_id=(\d+)', str(event.sender))
        event_self_id = match.group(1)
        if bot.self_id == event_self_id:
            pass
        elif bot.self_id == duel_player2[0]:
            await messagae_handle.send("不要让牛牛参加决斗啦...牛牛只想喝酒，呼...呼...")
        elif event_self_id == duel_player2[0]:
            await messagae_handle.send("左脚踩右脚也不能上天哦。")
        else:
            await messagae_handle.send(event_self_id)


@duel_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State) ->bool:
    await duel(duel_msg, bot, event, state)

class gagController:

    def add_victim(self, userID, gap):
        with open(f'./{userID}', 'w') as f:
            f.write(f'{time.time() + gap * 60}')
            # self.victim[userID]=time.time()+gap*60

    def check_victim(self, userID):
        try:
            with open(f'./{userID}', 'r') as f:
                lostTime = float(f.read())
                if lostTime > time.time():
                    return int(lostTime - time.time())
            os.remove(f"./{userID}")
            return False
        except:
            return False

    def process_raw_data(self, raw_txt):
        reslut = ''

        additionTable = [
            '',
            '....',
            # '~w♡',
            '~♡~'
        ]
        max_gap = 1
        for t in raw_txt:
            addChar = random.choice(additionTable)
            gap = 0
            while addChar != '' and gap < max_gap:
                gap += 1
                reslut += addChar
                addChar = random.choice(additionTable)
            reslut += t

        return reslut


gagControlPanel = gagController()

if __name__ == "__main__":
    gag = gagController()
    print(gag.process_raw_data('md, 功能写完仔细一想好淫乱啊艹'))