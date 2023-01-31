# Itachi Userbot - A telegram userbot.
# Copyright (C) 2021 Itachisann

# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY
# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see < https: // www.gnu.org/licenses/>.


import datetime
import json
import os
import time
from typing import Tuple

from telethon.events import StopPropagation
from telethon.tl import functions, types
from userbot import client
from userbot.core.events import NewMessage
from userbot.core.helpers import _humanfriendly_seconds, get_chat_link
from userbot.plugins import plugins_data

plugin_category = "status"
DEFAULT_UNMUTE_SETTINGS = types.InputPeerNotifySettings(
    show_previews=True,
    silent=False
)
DEFAULT_MUTE_SETTINGS = types.InputPeerNotifySettings(
    silent=True,
    mute_until=datetime.timedelta(days=365)
)


AFK = plugins_data.AFK
AFK.privates = plugins_data.load_data('userbot_afk_privates')
AFK.groups = plugins_data.load_data('userbot_afk_groups')
AFK.sent = plugins_data.load_data('userbot_afk_sent')
going_afk = "**Adesso sono AFK.**"
going_afk_reason = going_afk + "\n**Motivo:** __{reason}__"
not_afk = "`Non sono più AFK!`"
currently_afk = "🤍 **Al momento non sono disponibile, ti risponderò il prima possibile.**"
currently_afk_reason = (
    "🤍 **Al momento non sono disponibile, ti risponderò il prima possibile.\n\nMotivo: ** `{reason}`"
)


@client.createCommand(
    command=("approve [Utente]", plugin_category),
    outgoing=True, regex=r"approve(?: |$)(.+)?$"
)
async def approve(event: NewMessage.Event) -> None:
    users = await get_users(event)
    approved = []
    skipped = []
    with open('userbot/database/database.json') as json_file:
        data_read = json.load(json_file)
    if users:
        for user in users:
            href = await get_chat_link(user)
            if 'yourself' not in href:
                if user.verified or user.support or user.bot:
                    skipped.append(href)
                    continue
                if user.id in data_read['approved_users']:
                    skipped.append(href)
                else:
                    with open('userbot/database/database.json', 'w') as f:
                        approvedUsers = data_read['approved_users']
                        approvedUsername = data_read['approved_username']
                        approvedUsers.append(user.id)
                        approvedUsername.append('@'+user.username)
                        data = {}
                        data['approved_users'] = approvedUsers
                        data['approved_username'] = approvedUsername
                        f.write(json.dumps(data))
                    approved.append(href)
                    if "userbot_afk" in os.environ:
                        await client(functions.account.UpdateNotifySettingsRequest(
                            peer=user.id,
                            settings=DEFAULT_UNMUTE_SETTINGS
                        ))
    if approved:
        text = '✅ '+', '.join(approved) + " __approvato con successo__ "
        await event.answer(text, log=('pmpermit', text))
    if skipped:
        text = ', '.join(skipped) + " **  approvato.** "
        await event.answer(text)


@client.createCommand(
    command=("disapprove [Utente]", plugin_category),
    outgoing=True, regex=r"(?:un|dis)approv(?:a|e)(?: |$)(.+)?$"
)
async def disapprove(event: NewMessage.Event) -> None:
    users = await get_users(event)
    disapproved = []
    skipped = []
    with open('userbot/database/database.json') as json_file:
        data_read = json.load(json_file)
    if users:
        for user in users:
            href = await get_chat_link(user)
            if 'yourself' not in href:
                if user.id in data_read['approved_users']:
                    with open('userbot/database/database.json', 'w') as f:
                        approvedUsers = data_read['approved_users']
                        approvedUsername = data_read['approved_username']
                        approvedUsers.remove(user.id)
                        approvedUsername.remove('@'+user.username)
                        data = {}
                        data['approved_users'] = approvedUsers
                        data['approved_username'] = approvedUsername
                        f.write(json.dumps(data))
                    disapproved.append(href)
                    if "userbot_afk" in os.environ:
                        await client(functions.account.UpdateNotifySettingsRequest(
                            peer=user.id,
                            settings=DEFAULT_MUTE_SETTINGS
                        ))
                else:
                    skipped.append(href)
    if disapproved:
        text = '❌ '+', '.join(disapproved) + " __disapprovato con successo__ "
        await event.answer(text, log=('pmpermit', text))
    if skipped:
        text = ', '.join(skipped) + "** non è approvato!** "
        await event.answer(text)


@client.createCommand(
    command=("approved", plugin_category),
    outgoing=True, regex=r"approved$"
)
async def approved(event: NewMessage.Event) -> None:
    with open('userbot/database/database.json') as json_file:
        data_read = json.load(json_file)
    if data_read['approved_username']:
        text = "**Utenti approvati:**\n"
        text += ' - '.join([f'{i}' for i in data_read['approved_username']])
        await event.answer(text)
    else:
        await event.answer("`Ancora nessuno approvato..`")


async def get_users(event: NewMessage.Event) -> types.User or None:
    match = event.matches[0].group(1)
    users = []
    if match:
        matches, _ = await client.parse_arguments(match)
        for match in matches:
            try:
                entity = await client.get_entity(match)
                if isinstance(entity, types.User):
                    users.append(entity)
            except (TypeError, ValueError):
                pass
    elif event.is_private and event.out:
        users = [await event.get_chat()]
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        users = [await reply.get_sender()]
    return users


@client.createCommand(
    command="afk",
    outgoing=True, regex="(p)?afk(?: |$)(.*)?$"
)
async def awayfromkeyboard(event: NewMessage.Event) -> None:
    userbot_afk = os.environ.pop('userbot_afk', False)
    if userbot_afk == False:
        arg = event.matches[0].group(2)
        curtime = time.time().__str__()
        os.environ['userbot_afk'] = f"{curtime}/{event.chat_id}/{event.id}"
        os.environ['userbot_afk_private'] = "True" if event.matches[0].group(
            1) else "False"
        extra = await get_chat_link(event, event.id)
        log = ("afk", f"You just went AFK in {extra}!")
        if arg:
            arg = arg.strip()
            os.environ['userbot_afk_reason'] = arg
            await event.resanswer(
                going_afk_reason, plugin='afk', name='going_afk_reason',
                formats={'reason': arg}, log=log
            )
        else:
            await event.resanswer(
                going_afk, plugin='afk', name='going_afk', log=log
            )
        raise StopPropagation
    else:
        if event.from_scheduled or not userbot_afk:
            return
        os.environ.pop('userbot_afk_reason', None)
        _, chat, msg = userbot_afk.split('/')
        await client.delete_messages(int(chat), int(msg))

        def_text = "`Non hai ricevuto messaggi.`"
        pr_text = ''
        pr_log = ''
        gr_text = ''
        gr_log = ''

        if AFK.privates:
            total_mentions = 0
            to_log = []
            pr_log = "**Menzioni ricevute da chat private:**\n"
            for key, value in AFK.privates.items():
                await _update_notif_settings(key, value['PeerNotifySettings'])
                total_mentions += len(value['mentions'])
                msg = "  `{} menzioni da` [{}](tg://user?id={})"
                to_log.append(msg.format(
                    len(value['mentions']), value['title'], key
                ))

            pr_text = "`Ricevuti {} messaggi{} da {} chat private.`".format(
                *(await _correct_grammer(total_mentions, len(AFK.privates)))
            )
            pr_log = pr_log + "\n\n".join("  " + t for t in to_log)
        if AFK.groups:
            total_mentions = 0
            to_log = []
            gr_log = "\n**Menzioni ricevute dai gruppi:**\n"
            for key, value in AFK.groups.items():
                await _update_notif_settings(key, value['PeerNotifySettings'])
                total_mentions += len(value['mentions'])
                chat_msg_id = f"https://t.me/c/{key}/{value['unread_from']}"
                msg = f"[{value['title']}]({chat_msg_id}):"
                msg += "\n    `Menzioni:` "
                mentions = []
                for i in range(len(value['mentions'])):
                    msg_id = value['mentions'][i]
                    mentions.append(
                        f"[{i + 1}](https://t.me/c/{key}/{msg_id})")
                msg += ',   '.join(mentions) + '.'
                to_log.append(msg)

            gr_text = "`Ricevute {} menzioni{} da {} gruppi.`".format(
                *(await _correct_grammer(total_mentions, len(AFK.groups)))
            )
            gr_log = gr_log + "\n\n".join("  " + t for t in to_log)

        main_text = '\n\n'.join([pr_text, gr_text]).strip()
        status = await event.resanswer(
            not_afk, plugin='afk', name='not_afk',
            self_destruct=4
        )
        await event.answer(
            main_text or def_text,
            reply_to=status.id,
            self_destruct=4,
            log=("afk", '\n'.join([pr_log, gr_log]).strip() or def_text)
        )

        for chat, msg in AFK.sent.items():
            msgs = [m for m, _ in msg]
            await client.delete_messages(chat, msgs)
        AFK.privates.clear()
        AFK.groups.clear()
        AFK.sent.clear()


@client.createCommand(incoming=True, edited=False)
async def inc_listner(event: NewMessage.Event) -> None:
    with open('userbot/database/database.json') as json_file:
        data_read = json.load(json_file)
    sender = await event.get_sender()
    if event.from_scheduled or (isinstance(sender, types.User) and sender.bot):
        return

    afk = os.environ.get('userbot_afk', False)
    private_only = os.environ.get('userbot_afk_private', "False")
    if not (afk and (event.is_private or event.mentioned)):
        return
    if private_only == "True" and not event.is_private:
        return

    since = datetime.datetime.fromtimestamp(
        float(afk.split('/')[0]),
        tz=datetime.timezone.utc
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    reason = os.environ.get('userbot_afk_reason', False)
    elapsed = await _humanfriendly_seconds((now - since).total_seconds())
    chat = await event.get_chat()
    if event.is_private:
        await _append_msg(AFK.privates, chat.id, event.id)

    if chat.id in AFK.sent:
        if round((now - AFK.sent[chat.id][-1][1]).total_seconds()) <= 150:
            return
    if chat.id not in data_read['approved_users']:
        if reason:
            result = await event.resanswer(
                currently_afk_reason, plugin='afk', name='currently_afk_reason',
                formats={'elapsed': elapsed, 'reason': reason}, reply_to=None
            )
        else:
            result = await event.resanswer(
                currently_afk, plugin='afk', name='currently_afk',
                formats={'elapsed': elapsed}, reply_to=None
            )
    AFK.sent.setdefault(chat.id, []).append((result.id, result.date))


async def _append_msg(variable: dict, chat: int, event: int) -> None:
    with open('userbot/database/database.json') as json_file:
        data_read = json.load(json_file)
    if chat in variable:
        variable[chat]['mentions'].append(event)
    else:
        notif = await client(functions.account.GetNotifySettingsRequest(
            peer=chat
        ))
        notif = types.InputPeerNotifySettings(**vars(notif))
        if chat not in data_read['approved_users']:
            await _update_notif_settings(chat)
        async for dialog in client.iter_dialogs():
            if chat == dialog.entity.id:
                title = getattr(dialog, 'title', dialog.name)
                unread_count = dialog.unread_count
                last_msg = dialog.message.id
                break
        x = 1
        messages = []
        async for message in client.iter_messages(
            chat,
            max_id=last_msg
        ):
            if x >= unread_count:
                if not messages:
                    messages.append(message.id)
                break
            if not message.out:
                x = x + 1
                messages.append(message.id)
        variable[chat] = {
            'title': title,
            'unread_from': messages[-1],
            'mentions': [event],
            'PeerNotifySettings': notif
        }
        messages.clear()


async def _update_notif_settings(
    peer: int,
    settings: types.InputPeerNotifySettings = DEFAULT_MUTE_SETTINGS
) -> None:
    await client(functions.account.UpdateNotifySettingsRequest(
        peer=peer,
        settings=settings
    ))


async def _correct_grammer(
    mentions: int, chats: int
) -> Tuple[str, str, str, str]:
    a1 = "1" if mentions == 1 else mentions
    a2 = '' if mentions == 1 else ''
    a3 = "1" if chats == 1 else chats
    a4 = '' if chats == 1 else ''
    return a1, a2, a3, a4
