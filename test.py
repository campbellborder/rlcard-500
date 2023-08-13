import rlcard

env = rlcard.make('five-hundred')
game = env.game
state, player_id = env.reset()
game.round.print_scene()

env.step(1)
game.round.print_scene()

env.step(10)
game.round.print_scene()

env.step(1)
game.round.print_scene()

state, player = env.step(1)
game.round.print_scene()

env.step(1)
game.round.print_scene()