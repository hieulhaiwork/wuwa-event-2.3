import random
from tqdm import tqdm

CUBE_NUM = 6
CUBE_NAMES = ['jinhsi','changli','anh_lao_cong','shore','camellya','carlotta']
BOARD_LENGTH = 23

class Cube:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.position = 0
        self.finished_rank = 0 # Not completed yet. 1 for first rank, 2 for second rank,...
        self.log = []

    def __repr__(self):
        return f"Cube({self.name}, Pos:{self.position}, Rank:{self.finished_rank})"
    
def move(cube_name: str):
    if cube_name == "shore":
        return random.choice([2,3])
    return random.randint(1,3)

def apply_abilities_related_moving(cube: Cube, current_roll: int, board_state: list, is_last: bool, game_round: int):
    move_amount = current_roll
    cube.log.append(f"Rolled base: {current_roll}. Cube: {cube.name}")

    # carlotta: 28% x2
    if cube.name == 'carlotta':
        if random.random() < 0.28:
            move_amount *= 2
            cube.log.append(f"carlotta ability triggered! Move doubled to {move_amount}")
    
    # camellya: 50% +n move based on number of other cubes stack.
    if cube.name == 'camellya':
        if random.random() < 0.5 and game_round > 1:
            bonus_move = 0
            if 0 <= cube.position <= len(board_state):
                current_stack_camellya = board_state[cube.position]
                for other_cube_name in current_stack_camellya:
                    if other_cube_name != cube:
                        bonus_move += 1
            
            if bonus_move > 0:
                move_amount += bonus_move
                cube.log.append(f"camellya ability triggered! + {bonus_move}. Total: {move_amount}")

    if cube.name == "anh_lao_cong" and is_last:
        move_amount += 3
        cube.log.append(f"anh_lao_cong ability triggered! +3 move. Total: {move_amount}")

    return move_amount

# Handle changli ability: 65% move last if there is at least a cube below
def changli_ability(board_state, current_changli_position, verbose):
    if 0 <= current_changli_position < len(board_state):
        current_stack_changli = board_state[current_changli_position]
        changli_index = [i for i, cube in enumerate(current_stack_changli) if cube.name == "changli"]
        if len(changli_index) != 1:
            raise ValueError(f"There are more Changli cube in stack. Expected 1 but got {len(changli_index)}. Current position: {current_changli_position}")
        if changli_index[0] > 0:
            if random.random() < 0.65:
                if verbose:
                    print("Changli ability triggered!")
                return True
        return False

def jinhsi_ability(board_state, current_jinhsi_position, verbose):
    if 0 <= current_jinhsi_position < len(board_state):
        current_stack_jinhsi = board_state[current_jinhsi_position]
        jinhsi_zip = [(i, cube) for i, cube in enumerate(current_stack_jinhsi) if cube.name == "jinhsi"]
        if len(jinhsi_zip) != 1:
            raise ValueError(f"There are more Jinhsi cube in stack. Expected 1 but got {len(jinhsi_zip)}. Current position: {current_jinhsi_position}")
        (jinhsi_index, jinhsi_cube) = jinhsi_zip[0]
        if jinhsi_index != (len(current_stack_jinhsi) - 1):
            if random.random() < 0.4:
                current_stack_jinhsi.remove(jinhsi_cube)
                current_stack_jinhsi.append(jinhsi_cube)
                board_state[current_jinhsi_position] = current_stack_jinhsi
                if verbose:
                    print("Jinhsi ability triggered!")
                return board_state
        return board_state
            
def simulate(verbose=True):
    cubes = [Cube(i, CUBE_NAMES[i]) for i in range(CUBE_NUM)]

    # board_state: list of all cubes in the same position, arranged as stack
    board_state = [[] for _ in range(BOARD_LENGTH+1)]
    for cube in cubes:
        board_state[0].append(cube)

    next_rank = 1
    num_finished_cubes = 0
    game_round_count = 0
    is_changli_ability = False
    
    if verbose:
        print("----Race Start----")
        print(board_state)
    
    while num_finished_cubes < CUBE_NUM:
        game_round_count += 1
        if verbose:
            print("\n")
            print(f"\n--- Full Round {game_round_count} ---")
            print("\n")

        cubes_to_move_this_round = [cube for cube in cubes if cube.finished_rank == 0]
        if not cubes_to_move_this_round:
            break

        # random the origin orders
        random.shuffle(cubes_to_move_this_round)
        if is_changli_ability:
            changli_cube =  next((c for c in cubes_to_move_this_round if c.name == "changli"), None)
            if changli_cube:
                cubes_to_move_this_round.remove(changli_cube)
                cubes_to_move_this_round.append(changli_cube)
                is_changli_ability = False

        if verbose and cubes_to_move_this_round:
            print(f"Turn order for this round: {[cube.name for cube in cubes_to_move_this_round]}")
            print("\n")
        
        for i, cube_to_move in enumerate(cubes_to_move_this_round):
            if cube_to_move.finished_rank != 0:
                continue
            cube_to_move.log = []
            is_last = (i == len(cubes_to_move_this_round)-1)

            base_roll = move(cube_to_move.name)
            actual_move_distance = apply_abilities_related_moving(cube_to_move, base_roll, board_state, is_last, game_round_count)
            
            if verbose:
                print(cube_to_move.log)

            old_pos = cube_to_move.position
            new_pos = min(old_pos + actual_move_distance, BOARD_LENGTH)

            if game_round_count > 1:
                moving_party = []
                if 0 <= old_pos < BOARD_LENGTH:
                    stack_at_old_pos = board_state[old_pos]
                    idx_in_old_stack = stack_at_old_pos.index(cube_to_move)
                    moving_party = stack_at_old_pos[idx_in_old_stack:]
                    board_state[old_pos] = stack_at_old_pos[:idx_in_old_stack]
                    board_state[new_pos].extend(moving_party)


                if len(moving_party) == 1:
                    cube_to_move.position = new_pos

                    if cube_to_move.name == 'changli':
                        current_changli_position = new_pos

                    if cube_to_move.name == 'jinhsi':
                        current_jinhsi_position = new_pos

                    if cube_to_move.position >= BOARD_LENGTH and cube_to_move.finished_rank == 0:
                        cube_to_move.finished_rank = next_rank
                        next_rank += 1
                        num_finished_cubes += 1

                elif len(moving_party) > 1:
                    for cube in moving_party[::-1]:
                        cube.position = new_pos

                        if cube.name == 'changli':
                            current_changli_position = new_pos

                        if cube.name == 'jinhsi':
                            current_jinhsi_position = new_pos

                        if cube.position >= BOARD_LENGTH and cube.finished_rank == 0:
                            cube.finished_rank = next_rank
                            next_rank += 1
                            num_finished_cubes += 1
            else:
                if 0 <= old_pos < BOARD_LENGTH:
                    board_state[old_pos].remove(cube_to_move)
                    board_state[new_pos].append(cube_to_move)
                    cube_to_move.position = new_pos

                    if cube_to_move.name == 'changli':
                        current_changli_position = new_pos

                    if cube_to_move.name == 'jinhsi':
                        current_jinhsi_position = new_pos

                    if cube_to_move.position >= BOARD_LENGTH and cube_to_move.finished_rank == 0:
                        cube_to_move.finished_rank = next_rank
                        next_rank += 1
                        num_finished_cubes += 1

            
            if verbose:
                for i, state in enumerate(board_state):
                    print(f"{i}. {state}")
                print(f"\n")

        is_changli_ability = changli_ability(board_state, current_changli_position, verbose)
        board_state = jinhsi_ability(board_state, current_jinhsi_position, verbose)

    return cubes


if __name__ == "__main__":
    statistic_board = {
       name: 0 for name in CUBE_NAMES 
    }

    NUM_ITER = 1000000

    for _ in tqdm(range(NUM_ITER), desc="Num of iters:"):
        cubes = simulate(verbose=False)
        rank1_cube = [cube.name for cube in cubes if cube.finished_rank == 1][0]
        statistic_board[rank1_cube] += 1

    percentages = {name: (count / NUM_ITER) * 100 for name, count in statistic_board.items()}
    for name, percent in percentages.items():
        print(f"{name}: {percent:.2f}%")