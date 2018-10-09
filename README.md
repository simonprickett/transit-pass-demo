# Transit Pass Demo

## Introduction

A Transit pass demo system using Redis, Raspberry-Pi, Low Voltage Labs Traffic Light LEDs, RC522 RFID tags and associated reader hardware.  The code is a mixture of Python 3 and Node.js.

**TODO** Add an overview video...

## Types of Transit Passes

Imagine a transit system where users each have a smart card.  These cards each have a unique serial number.  In order to gain entry to the transit system a user's card must have a valid transit pass associated with it.  Exits from the system are not tracked.  In this example, the following types of pass exist:

* **Single Trip Pass:** This can be used for one entry / journey only.  It expires immediately after first use.
* **Ten Trip Pass:** This can be used for ten entries and doesn't expire until all ten have been used.
* **Two Hour Pass:** This can be used for an unlimited number of entries, and expires two hours after the first time it is used.

## Components and Architecture

There are four main components to the system:

### Sales Terminal 

Built with: 

* Python 3
* Raspberry Pi
* Three Arcade Buttons
* RFC522 Card Reader

The Sales Terminal allows mass transit riders to tap their transit card on the reader and select which of the available transit pass types they would like to add to their card.  They then tap the same card a second time to conclude the transaction.  The sales terminal uses spoken prompts to instruct the user, and provides different colored buttons that the user can press to select the type of pass that they wish to add.  The Sales Terminal will reject attempts to add a pass to a card that is already associated with a valid pass.  The Sales Terminal reports each successful issuing of a pass to the System Monitor component.

### Entry Gate

Built with: 

* Python 3
* Raspberry Pi
* Low Voltage Labs Traffic Light LEDs
* RFC522 Card Reader

The Entry Gate waits for a user to tap their card to the reader, indicating that they wish to enter the transit system and start a journey.  If the user's card is associated with a valid pass, the Entry Gate turns the entry light green and reports a successful entry to the System Monitor component.  For the first use of a two hour pass, the Entry Gate sets the pass expiry in the database to be 2 hours.  For each use of a ten use pass, the Entry Gate reduces the number of remaining trips available on the pass by one.  For a single use pass, the Entry Gate deletes the pass fom the database.  If a user presents a card that does not have a valid pass associated with it, the Entry Gate sounds an alarm and flashes the entry light red.  All attempts to enter the system are reported to the System Monitor component.

### System Monitor

Built with:

* Node.js

The System Monitor component receives messages from the Entry Gate and Sales Terminal components, displaying them in a log like format.

### Database & Pub/Sub Broker

Built with:

* Redis Labs Redis in the cloud

The Redis database is used to store card and pass details.  It manages the expiry time on the two hour pass and is a central data repository that the Sales Terminal and Entry Gate components read and write from.  The system also uses the Redis Pub/Sub messaging system to pass messages from the Sales Terminal and Entry Gate components which act as publishers to the System Monitor component which is a subscriber.
