#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants

import random
import logging


# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("ThePythonator")

ship_status = {}
ship_destination = {}

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"
        # Log ship info
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount)) 
        logging.info("Cell {} has {} halite.".format(ship.position, game_map[ship.position].halite_amount))
        logging.info("Ship {} has status: {}.".format(ship.id, ship_status[ship.id]))

        game_map[ship.position].mark_unsafe(ship)

        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                command_queue.append(ship.move(move))
                ship_destination[ship.id] = me.shipyard.position
                logging.info("RETURNING!!")
                continue
        elif ship.halite_amount >= constants.MAX_HALITE / 4:
            ship_status[ship.id] = "returning"
        
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        elif ship_status[ship.id] == "exploring":
            if ship.is_full:
                ship_status[ship.id] = "returning"
            elif game_map[ship.position].halite_amount <= constants.MAX_HALITE / 10:
                logging.info("EXPLORING!!")
                new_pos = ship.position
                for position in ship.position.get_surrounding_cardinals():
                    if game_map[position].is_occupied != True:
                        new_pos = position
                        break          
                if new_pos == ship.position:
                    command_queue.append(ship.stay_still())
                    logging.info("COLLECTING!!")
                    ship_destination[ship.id] = ship.position
                else:
                    command_queue.append(ship.move(game_map.naive_navigate(ship, new_pos)))
                    ship_destination[ship.id] = new_pos
            else:
                command_queue.append(ship.stay_still())
                logging.info("COLLECTING!!")
                ship_destination[ship.id] = ship.position
        else:
            ship_status[ship.id] = "exploring"
            logging.info("UNEXPECTED!!")

        # Set ship destination
        ship_destination[ship.id] = ship.position
        logging.info("Ship {} has destination: {}.".format(ship.id, ship_destination[ship.id]))

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    # game.turn_number <= 1 and
    if len(me.get_ships()) <= 3 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
