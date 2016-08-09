#-*- coding: utf-8 -*-
import unittest
import libtcodpy as libtcod

# import gui
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from UI import gui

# import gset
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from brrl_proto1 import game_settings as gset
from brrl_proto1 import Map


class Obstacle:
    def __init__(self, blocked=False):      
        self.blocked = blocked
        #fov 추가될 예정.

class Fighter:
    def __init__(self, hp, hpRegen, power, accuracy, defense):
        self.hp = hp
        self.hpRegen = hpRegen
        self.power = power
        self.accuracy = accuracy
        self.defense = defense

    def attack(self, target):
        if target is None:
            print "attack but no target!"
        else:            
            damage = self.power - target.fighterComponent.defense
            coin = libtcod.random_get_int(0,1,100)
            if coin < self.accuracy:
                target.fighterComponent.hp -= damage
                print ("Bonk!: your attack:", self.power, 
                       "but damage:", damage, 
                       'enemy hp:', target.fighterComponent.hp)
            else:
                print "miss!"
    
    # GameObject    로 바꿀까?
class ComponentOwner:
    def __init__(self, xInMap, yInMap, 
                 renderComponent=None, 
                 obstacleComponent=None, 
                 fighterComponent=None):
        self.xInMap = xInMap
        self.yInMap = yInMap
        self.renderComponent = renderComponent
        self.obstacleComponent = obstacleComponent
        self.fighterComponent = fighterComponent
    
    def moveInMap(self, x, y, mapObjs):
        print 'b:',self.xInMap, self.yInMap, ' ',
        
        canGo = True
        obstacle = None
        for obj in mapObjs:            
            if((obj.xInMap == self.xInMap + x and obj.yInMap == self.yInMap + y)
                and obj.obstacleComponent.blocked):
                    canGo = False
                    obstacle = obj
        if canGo:
            self.xInMap += x
            self.yInMap += y
            print 'f:',self.xInMap, self.yInMap, ' '            
        else:
            print "cannot move over blocked obstacle!"  
                 
        return obstacle
    

#1. 입력 준비
mouse = libtcod.Mouse()
key = libtcod.Key()

class Test_proto1(unittest.TestCase):
    def test_gameLoop(self):
        #창 초기화
        font = gui.Font('font.png', libtcod.FONT_LAYOUT_ASCII_INROW, 32, 2048)
        gset.setWindow(font, gset.WINDOW_WIDTH, gset.WINDOW_HEIGHT, 'test')
        gset.setLimitFps(gset.LIMIT_FPS)

        #맵에 스크린 배치
        map = Map.Map()
        terrainScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT, backAlphaRatio=1.0)
        mapObjScreen =  gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        npcScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        map.add(terrainScreen)
        map.add(mapObjScreen)
        map.add(npcScreen)
                
        #지형 생성
        tiles = [[None
                  for y in range(gset.WINDOW_HEIGHT)]
                    for x in range(gset.WINDOW_WIDTH)]
        for x in range(gset.WINDOW_WIDTH):
            for y in range(gset.WINDOW_HEIGHT):
                tile = gui.RenderObject(terrainScreen,
                                        'tile'+ str(x+y), str(x+y)[-1],
                                        x,y, backColor=libtcod.gray)
                tiles[x][y] = ComponentOwner(x,y, tile)

        #맵 구성요소 생성
        blockableObjs = []
        for i in range(13):
            tree = gui.RenderObject(mapObjScreen,
                                    'tree'+ str(i), u'●',
                                    i*2,i*2, foreColor=libtcod.darkest_red)
            mCompo = Obstacle(True)
            blockableObjs.append(ComponentOwner(i*2, i*2, tree,mCompo))
            
        #더미 적 생성
        initX = gset.WINDOW_WIDTH/2 - 5
        initY = gset.WINDOW_HEIGHT/2 - 5
        dummyActor = gui.RenderObject(npcScreen,'dummy',u'적', 
                                 initX,initY,
                                 foreColor=libtcod.blue)
        mapCompo = Obstacle(True)
        fighter = Fighter(30, 10, 10, 50, 1)
        dummy = ComponentOwner(initX, initY, dummyActor, mapCompo, fighter)
        blockableObjs.append(dummy)

        #유저 생성
        userScreen = gui.Screen(0,0, gset.WINDOW_WIDTH,gset.WINDOW_HEIGHT)
        initX = gset.WINDOW_WIDTH/2
        initY = gset.WINDOW_HEIGHT/2
        renderComponent = gui.RenderObject(userScreen,'user',u'나', 
                                 initX,initY,
                                 foreColor=libtcod.red)
        fighter = Fighter(100, 10, 5, 50, 0)
        user = ComponentOwner(initX, initY, renderComponent, fighterComponent=fighter)

        i = 0
        while not libtcod.console_is_window_closed():
            # 사용자 입력 함수 호출 a = waitInput()
            # 게임상태 변경 함수 호출 update(a)
            # 렌더링 함수 호출

            #1. 사용자 입력
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)

            #2. 게임 상태 변경(TODO: REFACTORING!!!!! 사용자 입력과 게임 상태 변경 디커플링하기?)
            #게임로직: 이동 막기
            #게임로직: 공격 - fighter 가진 객체끼리 하는거여
            # if의 조건은 함수 매개변수/ 안에 바뀌는 건...
            if key.vk == libtcod.KEY_UP:
                obstacle = user.moveInMap(0,-1, blockableObjs) 
                if obstacle is None:
                    map.y += 1    
                else:
                    if obstacle.fighterComponent is not None:
                        user.fighterComponent.attack(obstacle)
                    else:
                         print "but didn't try to break this shit!"

            elif key.vk == libtcod.KEY_DOWN:
                obstacle = user.moveInMap(0,1, blockableObjs) 
                if obstacle is None:
                    map.y -= 1    
                else:
                    if obstacle.fighterComponent is not None:
                        user.fighterComponent.attack(obstacle)
                    else:
                         print "but didn't try to break this shit!"

            elif key.vk == libtcod.KEY_LEFT:
                obstacle = user.moveInMap(-1,0, blockableObjs) 
                if obstacle is None:
                    map.x += 1  
                else:
                    if obstacle.fighterComponent is not None:
                        user.fighterComponent.attack(obstacle)
                    else:
                         print "but didn't try to break this shit!"

            elif key.vk == libtcod.KEY_RIGHT:
                obstacle = user.moveInMap(1,0, blockableObjs) 
                if obstacle is None:
                    map.x -= 1   
                else:
                    if obstacle.fighterComponent is not None:
                        user.fighterComponent.attack(obstacle)
                    else:
                         print "but didn't try to break this shit!"
            


            #3. 렌더링
            # ■■■버퍼 지우기■■■
            libtcod.console_clear(0) 

            map.renderAndBlit()
            userScreen.renderAndBlit()
            
            # ■■■버퍼 비우기■■■
            libtcod.console_flush() 

            
            i += 1
            if i == 10:
                break
            
            
    def test_attack(self):
        fighter = Fighter(30, 10, 10, 50, 1)
        fighter.attack


if __name__ == '__main__':
    unittest.main()
