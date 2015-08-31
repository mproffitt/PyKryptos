# PyKryptos
An application which uses [Mengenlehreuhr](https://en.wikipedia.org/wiki/Mengenlehreuhr) to try and crack
[Kryptos](https://en.wikipedia.org/wiki/Kryptos) section K4.

![Mengenlehreruhr](https://github.com/mproffitt/PyKryptos/blob/master/screenshots/clock.png)

This application uses the Berlin Clock (also known as the Set Theory Clock or Mengenlehreuhr), to try and decipher
the fourth part of Kryptos, which for 25 years has lain publically unbroken.

The attempt follows a years worth of research and testing against the cipher and is currently the one I consider to be
the most elegant and most likely.

The assumption against the cipher is that the key is in 2-3 parts.

1. That the key is time sensitive. This is the result of hints given in the previously revealed plaintext which
   states that characters 64-75 read BERLINCLOCK
2. That a 23 character alphabet is utilised. This is the result of examining sections k1-3 which offer a single mis-spelling per section
    * IQLUSION : ILLUSION
    * UNDERGRUUND : UNDERGROUND
    * DESPARATLY : DESPERATELY).

    These are then offerd as replacements using a list of tuples as `[(Q, L), (U, O), (A, E)]`
3. [OPTIONAL] - There could well be a keyword to the deciphering alphabet or the alphabet could be written top-down
   or bottom-up. Currently written without a keyword and bottom-up

## Requirements
This application has only been tested on Linux but should also work on Mac (Windows, possibly but I doubt it)

The application is written in the Python language and works with both 2.7 and 3.4

* Python
* curses

## Usage
Running the application is as simple as `python kryptos.py`
This will trigger using the application defaults starting at the current time.

### Advanced options

    --increment [minute|second]
      Update the clock by either minutes or seconds. (Default `second`)
    --speed (float)
      The interval at which to update the clock (Default `1.0`)
    --time (HH:MM:SS)
      Start the clock from a specific time given in 'HH:MM:SS'. (Default `now`)
    --alphabet (string)
      Use the custom alphabet. (Default `WXYZSTUVFGHIJKMNPQRABCD`)
    --replace (CR,CR,CR)
      Replace the following characters with their substitutes
      (Default `QL,UO,AE`)

## Note:
This is a **Proof of Concept (PoC)** only.
It is by no-means conclusive and is only being carried out as a part time exercise.

## History
* **31-08-2015** - *Bug fix - Cipher was returning invalid results when reading from the clock*.  
A problem existed with the cipher which resulted in the clock being read at least one minute behind, leading to duplicate sets of data being obtained and characters being encoded with an invalid set. Updated to accomodate this.
* **30-08-2015** - *Application refactoring, added unit tests for Decipher class*

## To-Do
* [M] Put some tests around the application
* [W] Add graphical controls for updating the alphabet, associated replacements, speed and increment

Contributions welcome.

## Contributors
[@200_success](http://codereview.stackexchange.com/users/9357/200-success)
who offered an initial refactoring of the clock on [Mengenlehreuhr in python](http://codereview.stackexchange.com/questions/101011/mengenlehreuhr-in-python)
