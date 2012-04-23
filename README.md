Ludum Dare 23!

I've been on a cycle of not-completing and completing these. This should be one of my good runs.

---

So here's the plan.

Tower defense game. ASCII console graphics.
The world starts out pitifully small, like 40x40 or something.
But it "pacmans" around like a torus (top of the map touches the bottom; left touches the right)
You are defending the north and south poles.
Enemies drop in from anywhere (except too near the poles, that'd be unfun).

And then the catch.
The map is growing.
After every wave new rows/columns of terrain just appear out of nowhere.
Spreading out your defenses.
Creating new weak points. 

---

Towers have a range of like 2-6 tiles around them. 
Upgrades sound like a good idea.

Submission Text:
---

I made an ASCII tower defense game, set upon a small asteroid.

An asteroid that, thanks to you, is becoming not so small.

It went well! I used Python and the Pytality console library that I made after Pyweek, which until now had not been put to the test of an LD48. And it worked really well.

The game came together much more rapidly than I'd expected, and seems pretty stable. Hopefully things are balanced well enough.

If you beat Hard difficulty, leave a comment! I'd like to know just how evil it is.

The game will try to run in either Pygame or native Windows console. If one of them fails, try the other - you can pass "pygame" or "winconsole" to it as a command-line argument to switch. 
