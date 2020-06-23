
import cv2
import paddlex
from paddlex.cls import transforms
from utils import *
from config import *
import imutils
import numpy as np

train_transforms = transforms.Compose([
    transforms.RandomCrop(crop_size=224),
    transforms.Normalize()
])

bg = None
model = paddlex.load_model('weights/final')
pygame.display.set_icon(Trollicon)


def process_gesture(thresholded):
    input_im = cv2.merge(
        [thresholded, thresholded, thresholded])
    result = model.predict(
        input_im, topk=5, transforms=train_transforms)
    gesture = result[0]['category']
    cv2.putText(input_im, gesture, (0, 20),
                cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 255, 0), 2)

    layout = np.zeros(input_im.shape)
    final = []
    for clas in CLASSES:
        for v in result:
            if v['category'] == clas:
                final.append(v['score'])
                break

    for (i, score) in enumerate(final):
        # construct the label text
        text = "{}: {:.2f}%".format(CLASSES[i], score * 100)

        w = int(score * 300)
        cv2.rectangle(layout, (7, (i * 35) + 5),
                      (w, (i * 35) + 35), (0, 0, 255), -1)
        cv2.putText(layout, text, (10, (i * 35) + 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (255, 255, 255), 2)

    return gesture, input_im, layout


def run_avg(image, aWeight):
    global bg
    if bg is None:
        bg = image.copy().astype('float')
        return

    cv2.accumulateWeighted(image, bg, aWeight)


def segment(image, threshold=25):
    global bg
    diff = cv2.absdiff(bg.astype('uint8'), image)

    thresholded = cv2.threshold(diff,
                                threshold,
                                255,
                                cv2.THRESH_BINARY)[1]

    (cnts, _) = cv2.findContours(thresholded.copy(),
                                 cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)

    if len(cnts) == 0:
        return
    else:
        segmented = max(cnts, key=cv2.contourArea)
        return (thresholded, segmented)


def setupRoomOne(all_sprites_list):
    wall_list = pygame.sprite.RenderPlain()

    for item in walls:
        wall = Wall(item[0], item[1], item[2], item[3], blue)
        wall_list.add(wall)
        all_sprites_list.add(wall)

    return wall_list


def setupGate(all_sprites_list):
    gate = pygame.sprite.RenderPlain()
    gate.add(Wall(282, 242, 42, 2, white))
    all_sprites_list.add(gate)
    return gate


def startGame():

    all_sprites_list = pygame.sprite.RenderPlain()
    block_list = pygame.sprite.RenderPlain()
    monsta_list = pygame.sprite.RenderPlain()
    pacman_collide = pygame.sprite.RenderPlain()
    wall_list = setupRoomOne(all_sprites_list)
    gate = setupGate(all_sprites_list)

    p_turn = 0
    p_steps = 0
    b_turn = 0
    b_steps = 0
    i_turn = 0
    i_steps = 0
    c_turn = 0
    c_steps = 0

    top, right, bottom, left = 90, 360, 285, 580

    Pacman = Player(w, p_h, 'images/Trollman.png')
    all_sprites_list.add(Pacman)
    pacman_collide.add(Pacman)

    Blinky = Ghost(w, b_h, 'images/Blinky.png')
    monsta_list.add(Blinky)
    all_sprites_list.add(Blinky)

    Pinky = Ghost(w, m_h, 'images/Pinky.png')
    monsta_list.add(Pinky)
    all_sprites_list.add(Pinky)

    Inky = Ghost(i_w, m_h, 'images/Inky.png')
    monsta_list.add(Inky)
    all_sprites_list.add(Inky)

    Clyde = Ghost(c_w, m_h, 'images/Clyde.png')
    monsta_list.add(Clyde)
    all_sprites_list.add(Clyde)

    for row in range(19):
        for column in range(19):
            if (row == 7 or row == 8) and (column == 8 or column == 9 or column == 10):
                continue
            else:
                block = Block(yellow, 4, 4)

                # Set a random location for the block
                block.rect.x = (30*column+6)+26
                block.rect.y = (30*row+6)+26

                b_collide = pygame.sprite.spritecollide(
                    block, wall_list, False)
                p_collide = pygame.sprite.spritecollide(
                    block, pacman_collide, False)
                if b_collide:
                    continue
                elif p_collide:
                    continue
                else:
                    # Add the block to the list of objects
                    block_list.add(block)
                    all_sprites_list.add(block)

    bll = len(block_list)
    score = 0
    num_frames = 0
    i = 0
    gesture = 'pause'
    thresholded = None

    camera = cv2.VideoCapture(0)

    while True:

        grabbed, frame = camera.read()
        if not grabbed:
            break

        frame = imutils.resize(frame, width=600)

        frame = cv2.flip(frame, 1)

        clone = frame.copy()

        (height, width) = frame.shape[:2]

        roi = frame[top:bottom, right:left]

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        if num_frames < 10:
            run_avg(gray, 0.5)

        else:
            hand = segment(gray)

            if hand is not None:
                (thresholded, segmented) = hand
                cv2.drawContours(
                    clone, [segmented + (right, top)], -1, (0, 0, 255))
        cv2.rectangle(clone, (left, top), (right, bottom), (0, 255, 0), 2)
        num_frames += 1

        if not thresholded is None:
            gesture, input_im, layout = process_gesture(thresholded)
            cv2.imshow('Thesholded', np.vstack([input_im, layout]))
        cv2.imshow('Video Feed', clone)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        if gesture == 'left':
            Pacman.changespeed(-30, 0)
        if gesture == 'right':
            Pacman.changespeed(30, 0)
        if gesture == 'up':
            Pacman.changespeed(0, -30)
        if gesture == 'down':
            Pacman.changespeed(0, 30)
        if gesture == 'pause':
            Pacman.changespeed(0, 0)

        Pacman.update(wall_list, gate)

        returned = Pinky.changespeed(
            Pinky_directions, False, p_turn, p_steps, pl)
        p_turn = returned[0]
        p_steps = returned[1]
        Pinky.changespeed(Pinky_directions, False, p_turn, p_steps, pl)
        Pinky.update(wall_list, False)

        returned = Blinky.changespeed(
            Blinky_directions, False, b_turn, b_steps, bl)
        b_turn = returned[0]
        b_steps = returned[1]
        Blinky.changespeed(Blinky_directions, False, b_turn, b_steps, bl)
        Blinky.update(wall_list, False)

        returned = Inky.changespeed(
            Inky_directions, False, i_turn, i_steps, il)
        i_turn = returned[0]
        i_steps = returned[1]
        Inky.changespeed(Inky_directions, False, i_turn, i_steps, il)
        Inky.update(wall_list, False)

        returned = Clyde.changespeed(
            Clyde_directions, 'clyde', c_turn, c_steps, cl)
        c_turn = returned[0]
        c_steps = returned[1]
        Clyde.changespeed(Clyde_directions, 'clyde', c_turn, c_steps, cl)
        Clyde.update(wall_list, False)

        # See if the Pacman block has collided with anything.
        blocks_hit_list = pygame.sprite.spritecollide(Pacman, block_list, True)

        # Check the list of collisions.
        if len(blocks_hit_list) > 0:
            score += len(blocks_hit_list)

        screen.fill(black)

        wall_list.draw(screen)
        gate.draw(screen)
        all_sprites_list.draw(screen)
        monsta_list.draw(screen)

        text = font.render('Score: '+str(score)+'/'+str(bll), True, red)
        screen.blit(text, [10, 10])

        if score == bll:
            doNext('Congratulations, you won!', 145, all_sprites_list,
                   block_list, monsta_list, pacman_collide, wall_list, gate)

        monsta_hit_list = pygame.sprite.spritecollide(
            Pacman, monsta_list, False)

        if monsta_hit_list:
            doNext('Game Over', 235, all_sprites_list, block_list,
                   monsta_list, pacman_collide, wall_list, gate)

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
        try:
            pygame.display.flip()
        except Exception as e:
            return
        clock.tick(10)


def doNext(message, left, all_sprites_list, block_list, monsta_list, pacman_collide, wall_list, gate):
    while True:
        try:
            # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if event.key == pygame.K_RETURN:
                        del all_sprites_list
                        del block_list
                        del monsta_list
                        del pacman_collide
                        del wall_list
                        del gate
                        startGame()

            # Grey background
            w = pygame.Surface((400, 200))  # the size of your rect
            w.set_alpha(10)                # alpha level
            w.fill((128, 128, 128))           # this fills the entire surface
            screen.blit(w, (100, 200))    # (0,0) are the top-left coordinates

            #Won or lost
            text1 = font.render(message, True, white)
            screen.blit(text1, [left, 233])

            text2 = font.render('To play again, press ENTER.', True, white)
            screen.blit(text2, [135, 303])
            text3 = font.render('To quit, press ESCAPE.', True, white)
            screen.blit(text3, [165, 333])

            pygame.display.flip()

            clock.tick(10)
            
        except Exception as e:
            break


if __name__ == '__main__':

    pl = len(Pinky_directions)-1
    bl = len(Blinky_directions)-1
    il = len(Inky_directions)-1
    cl = len(Clyde_directions)-1

    pygame.init()

    screen = pygame.display.set_mode([606, 606])

    pygame.display.set_caption('Pacman')

    background = pygame.Surface(screen.get_size())

    background = background.convert()

    background.fill(black)

    clock = pygame.time.Clock()

    pygame.font.init()
    font = pygame.font.Font('src/freesansbold.ttf', 24)

    startGame()

    pygame.quit()
