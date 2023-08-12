import rlcard

env = rlcard.make('five-hundred')
state, player_id = env.reset()
print(player_id)
print(state)
