#-*- coding: utf-8 -*-
import libtcodpy as libtcod
#네임스페이스 libtcodpy를 py빼고 쓸 수 있다.
 
print 'hello world!'
print u'새로운 시작' #  <--나가 고걸 몰랐었네!!

#actual size of the window
SCREEN_WIDTH = 30
SCREEN_HEIGHT = 30

LIMIT_FPS = 20 # 20 frames-per-second maximum


libtcod.console_set_custom_font( 'font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python + libtcod tutorial', False)

libtcod.sys_set_fps(LIMIT_FPS)

import test1
test1.outf()

mouse = libtcod.Mouse()
key = libtcod.Key()

x = 0
y = 0
def moveMe():
    global key, x,y

    if key.vk == libtcod.KEY_UP:
        y -= 1 
    elif key.vk == libtcod.KEY_DOWN:
        y += 1 
    elif key.vk == libtcod.KEY_LEFT:
        x -= 1 
    elif key.vk == libtcod.KEY_RIGHT:
        x += 1
    elif key.c == ord('+'):
        libtcod.console_init_root(40, 40, 'python + libtcod tutorial', False)
    elif key.c == ord('-'):
        libtcod.console_init_root(10, 10, 'python + libtcod tutorial', False)

offscreen_console = libtcod.console_new(15, 15)
offcon = libtcod.console_new(10,10)


def printJump(actor='ass'):
    print actor + ' jumpu'

def printRun(actor='ass'):
    print actor + ' run'

def printPoop(actor='ass'):
    print actor + ' shit...'

class Who:
    def __init__(self, name):
        self.name = name

    def jump(self):
        print self.name + ' jump'

    def run(self):
        print self.name + ' run'

    def poop(self):
        print self.name + ' poop'

############################## 커맨드 패턴 ##############################
# 이 패턴을 이용해서 유저와 ai의 입력 인터페이스를 동일하게 설정할 수 있다.

class Jump:
    def execute(self, who):
        printJump()
        who.jump()

class Run:
    def execute(self, who):
        printRun()
        who.run()

class Poop:
    def execute(self, who):
        printPoop()
        who.poop()

class InputHandler:
    def __init__(self, btnX, btnY, btnZ):
        self.btnX = btnX
        self.btnY = btnY
        self.btnZ = btnZ

    def handleInput(self):
        if key.vk == libtcod.KEY_UP:
            return self.btnX
        elif key.vk == libtcod.KEY_LEFT:
            return self.btnY
        elif key.vk == libtcod.KEY_RIGHT:
            return self.btnZ

###########################################################################

inputHandler = InputHandler(Jump(), Run(), Poop())


######################## 함수를 쓰는 커맨드 패턴 #########################
# 사실 패턴도 아냐 ㅋㅋ 개쩐당
class FInputHandler:
    def __init__(self, btnX, btnY, btnZ):
        self.btnX = btnX
        self.btnY = btnY
        self.btnZ = btnZ

    def handleInput(self):
        if key.vk == libtcod.KEY_UP:
            return self.btnX
        elif key.vk == libtcod.KEY_LEFT:
            return self.btnY
        elif key.vk == libtcod.KEY_RIGHT:
            return self.btnZ
########################################################################
fiHandler = FInputHandler(printJump, printRun, printPoop)

i = 0
#이게 바로 게임 루프가 된다... 사용자입력->게임 상태 변화
#최대 FPS는 LIMIT_FPS만큼 되고 그 FPS마다 렌더링한다.
while not libtcod.console_is_window_closed() :
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
    #이벤트를 체크하기 시작하니까 게임이 크래쉬되지 않는다.

############### 함수를 이용한 커맨드 패턴 ###############
    command = fiHandler.handleInput()
    if command is not None:
        command()
        command('he')
#######################################################

    libtcod.console_set_default_foreground(0, libtcod.white)

    #libtcod.console_put_char(0, 1, 1, ord (u'test'), libtcod.BKGND_NONE)

    libtcod.console_print(0, 1, 2, u'예를 들면 이런 식으로 한국어를 볼 수 있습니다')
    libtcod.console_print(0, 1, 3, u'1234567890abc\ndefghijklmnopqrstuv\nwxyz;!@#$%^&*()_+|')
    libtcod.console_print(0, 1, 5, u'###############')
    libtcod.console_print(0, 1, 6, u'#.............#')
    libtcod.console_print(0, 1, 7, u'#.............#')
    libtcod.console_print(0, 1, 8, u'#....나....T...#')
    libtcod.console_print(0, 1, 9, u'#.............#')
    libtcod.console_print(0, 1, 10, u'#.............#')
    libtcod.console_print(0, 1, 11, u'###############')
    
    #키보드로 입력받아서 움직이기
    '''
    command = inputHandler.handleInput()
    if command is not None:
        command.execute(Who('yee'))
    '''
    

    libtcod.console_set_default_foreground(0, libtcod.yellow) #노오랗게.
    libtcod.console_print(0, x,y, u'나')
    #나만의 렌더링 함수를 만들기 위해 한꺼풀 덮어 씌울 필요가 있다.

    libtcod.console_print(0, 1, 15, str(i))

    
    libtcod.console_set_default_background(offscreen_console, libtcod.red)
    libtcod.console_clear(offscreen_console)
    libtcod.console_blit(offscreen_console, 0,0,10,10, 0 ,5,5, 100/255.0, 0.5)
    #확대는 없다: dstW,H가 원래 콘솔보다 더 크면 더 큰건 그냥 안 그려줘
    #dstW,H가 0이면 원래 콘솔 크기대로 그랴줌

    libtcod.console_set_default_background(offcon, libtcod.red)
    libtcod.console_set_default_foreground(offcon, libtcod.black)
    libtcod.console_clear(offcon)
    libtcod.console_print(offcon, 2, 2, 'wtf??')
    libtcod.console_blit(offcon, 0,0,0,0, 0 ,0,0, 1, 0.5)
    #console_blit는 rootconsole에만 가능한 거 같다?
    #왜 다른 콘솔에는 시바 출력이 안되냐? ㅄ같넹
    
    libtcod.console_flush() #이거 없으면 출력이 안 돼.

    libtcod.console_print(0, 5, 15, str(i)) 
    i += 1

