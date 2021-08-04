#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-07-28
# @Filename: onoff.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio

import click
from clu.command import Command

from lvmnps.actor.commands import parser
from lvmnps.exceptions import NpsActorError



async def switch_control(switches: PowerSwitch, on: bool, name: str, portnum: int):

    try:
        tasks = []
        for switch in switches:
            tasks.append(asyncio.create_task(switch.setState(on, name, portnum)))

        await asyncio.gather(*tasks)

        status = {}
        for switch in switches:
            # status |= await switch.statusAsJson(name, portnum) works only with python 3.9
            status = dict(list(status.items()) +
                          list((await switch.statusAsJson(name, portnum)).items()))

    except NpsActorError as err:
        return {str(err)}

    return status


@parser.command()
@click.argument("NAME", type=str, default="")
@click.argument("PORTNUM", type=int, default=0)
async def on(command: Command, switches: PowerSwitch, name: str, portnum: int):
    """Turn on the Outlet"""

    command.info(STATUS=await switch_control(switches, True, name, portnum))

    return command.finish(text="done")


@parser.command()
@click.argument("NAME", type=str, default="")
@click.argument("PORTNUM", type=int, default=0)
async def off(command: Command, switches: PowerSwitch, name: str, portnum: int):
    """Turn off the Outlet"""

    command.info(STATUS=await switch_control(switches, False, name, portnum))

    return command.finish(text="done")


@parser.command()
@click.argument("NAME", type=str, default="")
async def onall(command: Command, switches: PowerSwitch, name: str):
    """Turn on all Outlet"""

    command.info(STATUS=await switch_control(switches, True, 0, name))

    return command.finish(text="done")


@parser.command()
@click.argument("NAME", type=str, default="")
async def offall(command: Command, switches: PowerSwitch, name: str):
    """Turn off all Outlet"""

    command.info(STATUS=await switch_control(switches, False, 0, name))

    return command.finish(text="done")
