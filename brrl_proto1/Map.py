#-*- coding: utf-8 -*-


from UI import gui


class Map(gui.ScreenManager):
    '''
    Screen 여러개를 모아놓은 클래스다.
    루트 콘솔(창)을 기준으로 하는 좌표를 자체적으로 가져서
    주인공을 기준으로 움직이게 할 수 있다.
    '''
    def __init__(self, x=0, y=0):
        ''' 창, 혹은 루트콘솔이 기준인 좌표(x,y)다. '''
        gui.ScreenManager.__init__(self)
        self.x = x
        self.y = y

    def blitAll(self):
        '''
        Map에 포함된 Screen을 blit할 때
        Screen의 좌표에 Map의 좌표만큼 더해서 blit한다.
        '''
        for screen in self._screenList:
            screen.blit(self.x, self.y)

    def renderAndBlit(self):
        '''
        맵에 포함된 모든 스크린을
        렌더링하고 루트콘솔에 블리트한다.
        '''
        for screen in self._screenList:
            screen.renderAndBlit(self.x, self.y)
