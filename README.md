# randbeacon
a lights display that reads the values from NIST's Randomness Beacon

We are using the [NIST Randomness Beacon v2](https://csrc.nist.gov/projects/interoperable-randomness-beacons/beacon-20) which generates truly random bitstrings once a minute. 

> A “randomness beacon” is a timed source of public randomness. It pulsates fresh randomness at expected times, making it available to the public

I think its cool that theres something in this world called a beacon.


### The design

we want brightness to be relatively static. lets just play with on/off and hue? will the colors just even out to be mush? 

ok first thing - when the beacon updates, i want some animation to play. A pulse from a beacon is cool i think. however i dont want it to be super distracting. 

I think the light should be somewhat dynamic. we could scan through values, and i think that could be cool. we have 64 values and 60 seconds in a minute. we could display one new value each time.

on the minute, we could display a quick sequence of white on-offs for the current time. because seconds wont matter we can divide the unix time by 60 and then cast to 8 bits? and play them really rapidly.

we only have 64 values between 0-255


lets do the first 2 bits represent the brightness, say only between 75-100%

we can just `value >> 6` to get those two bits isolated

then we want it to be between, ok lets make it easy - 50 and 100 %

that would just be 

1001 1111 50% = 159
0xx0 0000     = 0 - 96

so lets bring back up with `(value >> 6) << 5`

the last 6 bits represent hue, shifted up by two

this is a mask with `(value & 63) << 2`

