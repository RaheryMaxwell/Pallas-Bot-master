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


bulbus_oris_player = defaultdict(list)
role_cache = defaultdict(lambda : defaultdict(str))


async def am_I_admin(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    info = await get_bot(str(event.self_id)).call_api('get_group_member_info', **{
        'user_id': event.self_id,
        'group_id': event.group_id
    })
    role = info['role']
    role_cache[event.self_id][event.group_id] = role
    return role == 'admin' or role == 'owner'


async def am_I_admin_by_cache(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    role = role_cache[event.self_id][event.group_id]
    return role == 'admin' or role == 'owner'


async def participate_in_bulbus_oris(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    '''
    牛牛自己是否会被口球
    显然是不会的！
    '''
    return False


async def bulbus_oris(messagae_handle, bot: Bot, event: GroupMessageEvent, state: T_State):
    alco = ('长岛冰茶', '伏特加马天尼', '遗言', '杏仁酸', '盘尼西林', '血腥玛丽', '尼格罗尼', '古典', '信', '梦中旅途', '牛奶')
    type_msg = alco[random.randint(0, len(alco) - 1)]
    partin = participate_in_bulbus_oris(bot, event, state)
    if partin:
        bulbus_oris_player[event.group_id] = [event.self_id, event.user_id, ]
    else:
        bulbus_oris_player[event.group_id] = [event.self_id, ]
    await messagae_handle.send(
        f'勇士啊，既然你对前方的旅途执迷不悟，那么请饮下我为你调好的这杯《{type_msg}》，算是我对你未来的祝福。以及...我会在往世书中写下你的名字。')

    async def let_the_bullets_fly():
        await asyncio.sleep(random.randint(5, 15))

    await let_the_bullets_fly()

    await get_bot(str(event.self_id)).call_api('set_group_ban', **{
        'user_id': event.user_id,
        'group_id': event.group_id,
        'duration': random.randint(10, 15) * 60
    })

    await messagae_handle.finish("再见。")


async def is_bulbus_oris_msg(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    if event.get_plaintext().strip() in ['牛牛口球']:
        admin = await am_I_admin(bot, event, state)
        return admin
    return False

bulbus_oris_msg = on_message(
    priority=4,
    block=True,
    rule=Rule(is_bulbus_oris_msg),
    permission=permission.GROUP
)


@bulbus_oris_msg.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State) -> bool:
    await bulbus_oris(bulbus_oris_msg, bot, event, state)


