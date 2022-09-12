import rclpy, math, time, random, decimal
from rclpy.node import Node
from geometry_msgs.msg import Twist
from .laser import LaserSub

class VelocidadePub(Node):

    def __init__(self):
        # Criar publisher
        super().__init__('velocidadepub')
        self.velocity_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        timer_period = 0.01
        self.timer = self.create_timer(timer_period, self.movimenta)
        self.vel_msg = Twist()
        self.vel_msg.linear.x = 0.0  
        self.vel_msg.linear.y = 0.0 
        self.vel_msg.linear.z = 0.0  
        self.vel_msg.angular.x = 0.0
        self.vel_msg.angular.y = 0.0  
        self.vel_msg.angular.z = 0.0

    def movimenta(self, tipoMovimento):
        if(tipoMovimento == 1):
            self.andaFrente()
        elif(tipoMovimento == 2):
            self.andaEsquerda()
        elif(tipoMovimento == 3):
            self.andaDireita()
        elif(tipoMovimento == 4):
            self.viraEsquerda()
        elif(tipoMovimento == 5):
            self.viraDireita()
        elif(tipoMovimento == 6):
            self.re()
        elif(tipoMovimento == 7):
            self.rodar90()
        elif(tipoMovimento == 8):
            self.para()

    def para(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 0.0

        self.velocity_publisher.publish(move_cmd)
        self.get_logger().info('Parado.')

    def andaFrente(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.08
        move_cmd.angular.z = 0.0

        self.velocity_publisher.publish(move_cmd)
        self.get_logger().info('Andando para frente com velocidade 0.1')

    def andaEsquerda(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.1
        move_cmd.angular.z = 0.1

        self.velocity_publisher.publish(move_cmd)
        self.get_logger().info('Andando para esquerda com velocidade 0.1')

    def andaDireita(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.1
        move_cmd.angular.z = -0.1

        self.velocity_publisher.publish(move_cmd)
        self.get_logger().info('Andando para direita com velocidade 0.1')

    def viraEsquerda(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 0.2

        self.velocity_publisher.publish(move_cmd)
        self.get_logger().info('Virando para esquerda com velocidade 0.2')

    def viraDireita(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = -0.2

        self.velocity_publisher.publish(move_cmd)
        self.get_logger().info('Virando para direita com velocidade 0.2')

    def re(self):
        move_cmd = Twist()
        move_cmd.linear.x = -0.1
        move_cmd.angular.z = 0.0

        self.velocity_publisher.publish(move_cmd)
        self.get_logger().info('Dando ré com velocidade 0.1')

    def rodar90(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = -0.5

        self.velocity_publisher.publish(move_cmd)
        self.get_logger().info('Rotacionando 90 graus para direita')

def calcularDirecao(laser):
    print('---------------------Escolhendo direção...')
    somaDireita = (laser.nordeste + laser.leste)
    somaEsquerda = (laser.noroeste + laser.oeste)
    print('Soma esquerda: ' + str(somaEsquerda) + ' - Soma direita: ' + str(somaDireita))

    #if((laser.noroeste + laser.oeste + laser.sudoeste) > (laser.nordeste + laser.leste + laser.sudeste)):
    if(somaEsquerda > somaDireita):
        print('diff: ', str(somaEsquerda - somaDireita))
        #se a diferença de espaço entre os dois lados for pequena -> escolhe aleatoriamente
        if((somaEsquerda - somaDireita) <= 0.1): 
            aleat = random.randint(0, 1)
            print('aleat = ', str(aleat))
            if(aleat == 0):
                return 4
            else:
                return 5
        else:
            return 4
    else:
        print('diff: ', str(somaDireita - somaEsquerda))
        #se a diferença de espaço entre os dois lados for pequena -> escolhe aleatoriamente
        if((somaDireita - somaEsquerda) <= 0.1): 
            aleat = random.randint(0, 1)
            print('aleat = ', str(aleat))
            if(aleat == 0):
                return 4
            else:
                return 5
        else:
            return 4

def verificaSeguranca(limite, grauInicio, grauFinal, laser):
    contPerigo = 0
    incremento = 1
    if(grauInicio > grauFinal):
        incremento = -1
    for x in range(grauInicio, grauFinal, incremento):
        if(laser.msg.ranges[x] < limite):
            contPerigo += 1

    print('Verificando entre ' + str(grauInicio) + ' e ' + str(grauFinal) + ' -> ' + str(limite) + ' = ' + str(contPerigo))
    if(contPerigo >= 12):
        return False
    return True


def main(args=None):
    rclpy.init(args=args)

    laser = LaserSub()
    velocidade = VelocidadePub()

    ultimoMov = 1
    contLoop = 0

    ultimoNoroeste = -1.0
    ultimoNordeste = -1.0

    ehCurva = 0
    loopRestCurva = 50
    loopUltimaCurva = 0

    while(True):
        rclpy.spin_once(laser)
        
        andarEsquerda = 2
        andarDireita = 3
        virarEsquerda = 4
        virarDireita = 5
        re = 6
        rodar90graus = 7
        parar = 8

        tipoMovimento = 1 #andar pra frente


        # seguroOeste = (laser.oeste > 0.10 and laser.oeste != 0.0) or laser.oeste == math.inf
        # seguroNoroeste = (laser.noroeste > 0.25 and laser.noroeste != 0.0) or laser.noroeste == math.inf
        # seguroNorNoroeste = (laser.nornoroeste > 0.27 and laser.nornoroeste != 0.0) or laser.nornoroeste == math.inf
        # seguroNorte = (laser.norte > 0.3 and laser.norte != 0.0) or laser.norte == math.inf
        # seguroNorNordeste = (laser.nornordeste > 0.27 and laser.nornordeste != 0.0) or laser.nornordeste == math.inf
        # seguroNordeste = (laser.nordeste > 0.25 and laser.nordeste != 0.0) or laser.nordeste == math.inf
        # seguroLeste = (laser.leste > 0.10 and laser.leste != 0.0) or laser.leste == math.inf

        seguroOeste = verificaSeguranca(0.22, 90, 60, laser)
        seguroNoroeste = verificaSeguranca(0.25, 60, 30, laser)
        seguroNorNoroeste = verificaSeguranca(0.27, 30, 0, laser)
        seguroNorte = (laser.norte > 0.3 and laser.norte != 0.0) or laser.norte == math.inf
        seguroNorNordeste = verificaSeguranca(0.27, 359, 330, laser)
        seguroNordeste = verificaSeguranca(0.25, 330, 300, laser)
        seguroLeste = verificaSeguranca(0.22, 300, 270, laser)
        
        print('')
        print('oeste: ' + str(round(laser.oeste, 3)) + ' - nor-noroeste: '+ str(round(laser.nornoroeste, 3)) +
            ' - noroeste: ' + str(round(laser.noroeste, 3)) + ' - norte: ' + str(round(laser.norte, 3)) + 
            ' - nordeste: ' + str(round(laser.nordeste, 3)) + ' nor-nordeste: '+ str(round(laser.nornordeste, 3)) +
            ' - leste: ' + str(round(laser.leste, 3))) 
        print('oeste: ' + str(seguroOeste)  + ' - noroeste: ' + str(seguroNoroeste) + 
            ' - nor-noroeste: ' + str(seguroNorNoroeste) + ' - norte: ' + str(seguroNorte) + 
            ' - nor-nordeste: ' + str(seguroNorNordeste)+ ' - nordeste: ' + str(seguroNordeste) + 
            ' - leste: ' + str(seguroLeste))
        print('')

        tratouPerigo = False
        # if(seguroNorte == False):
        #     somaDireita = (laser.nordeste + laser.leste)
        #     somaEsquerda = (laser.noroeste + laser.oeste)
        #     print('Soma esquerda: ' + str(somaEsquerda) + ' - Soma direita: ' + str(somaDireita))

        #     #if((laser.noroeste + laser.oeste + laser.sudoeste) > (laser.nordeste + laser.leste + laser.sudeste)):
        #     if(somaEsquerda > somaDireita):
        #         print('diff: ', str(somaEsquerda - somaDireita))
        #         #se a diferença de espaço entre os dois lados for pequena -> escolhe aleatoriamente
        #         if((somaEsquerda - somaDireita) <= 0.1): 
        #             aleat = random.randint(0, 1)
        #             print('aleat = ', str(aleat))
        #             if(aleat == 0):
        #                 tipoMovimento = virarEsquerda
        #             else:
        #                 tipoMovimento = virarDireita
        #         else:
        #             tipoMovimento = virarEsquerda
        #     else:
        #         tipoMovimento = virarDireita
            
        #     tratouPerigo = True
        # elif(seguroNoroeste == False):
        #     tipoMovimento = virarDireita
        #     tratouPerigo = True
        # elif(seguroNordeste == False):
        #     tipoMovimento = virarEsquerda
        #     tratouPerigo = True
        # elif(seguroNorNoroeste == False):
        #     tipoMovimento = virarDireita
        #     tratouPerigo = True
        # elif(seguroNorNordeste == False):
        #     tipoMovimento = virarEsquerda
        #     tratouPerigo = True

        # if(seguroNorte == False or 
        #     seguroNorNoroeste == False or 
        #     seguroNoroeste == False or 
        #     seguroNorNordeste == False or 
        #     seguroNordeste == False):
        #     tipoMovimento = calcularDirecao(laser)
        #     tratouPerigo = True

        if(seguroNoroeste == False or seguroNorNoroeste == False):
            tipoMovimento = virarDireita
            tratouPerigo = True 
        elif(seguroNordeste == False or seguroNorNordeste == False):
            tipoMovimento = virarEsquerda
            tratouPerigo = True
        elif(seguroNorte == False or seguroNorNordeste == False or seguroNordeste == False or 
            seguroNorNoroeste == False or seguroNoroeste == False):
            tipoMovimento = calcularDirecao(laser)
            tratouPerigo = True
        else:
            somaTotalDireita = laser.leste
            somaTotalEsquerda = laser.oeste
            print('Soma total esquerda: ' + str(somaTotalEsquerda) + ' - Soma total direita: ' + str(somaTotalDireita))
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

            # if(seguroNoroeste and seguroOeste):
            #     tipoMovimento = virarEsquerda
            # elif(seguroNoroeste and seguroNorNoroeste and seguroNorte):
            #     tipoMovimento = 1 

            #tipoMovimento = virarDireita
            
            # if((contLoop - loopUltimaCurva) >= 75 and ehCurva == 0 and 
            #     ((somaTotalEsquerda >= 0.5 and somaTotalDireita >= 0.2) or 
            #     (somaTotalDireita >= 0.5 and somaTotalEsquerda >= 0.2))):
            #     #if(random.randint(1, 10000) % 4 == 0):
            #     rand = random.randint(4, 5)
            #     print('rand:', rand)
            #     tipoMovimento = rand
            #     tratouPerigo = True  #criar nova flag pra isso
            #     ehCurva = rand
            #     loopRestCurva = 15
            #     loopUltimaCurva = contLoop

            if((contLoop - loopUltimaCurva) >= 50 and ehCurva == 0):
                if(somaTotalEsquerda >= 0.5 and somaTotalDireita >= 0.2):
                    tipoMovimento = virarEsquerda
                    tratouPerigo = True  #criar nova flag pra isso
                    ehCurva = virarEsquerda
                    loopRestCurva = 15
                    loopUltimaCurva = contLoop
                elif(somaTotalDireita >= 0.5 and somaTotalEsquerda >= 0.2):
                    tipoMovimento = virarDireita
                    tratouPerigo = True  #criar nova flag pra isso
                    ehCurva = virarDireita
                    loopRestCurva = 15
                    loopUltimaCurva = contLoop

            # if(seguroLeste and seguroNordeste and (contLoop - loopUltimaCurva) >= 50 and ehCurva == 0):
            #     tipoMovimento = virarDireita
            #     tratouPerigo = True  #criar nova flag pra isso
            #     ehCurva = virarDireita
            #     loopRestCurva = 15
            #     loopUltimaCurva = contLoop

        # se estiver indo reto, a cada 3 loops faz correção para se manter no centro
        if(tipoMovimento == 1 and (contLoop % 3) == 0):
            print('corrigindo...')
            
            if(laser.leste > laser.oeste and laser.nordeste >= 0.5): #mais espaço na direita
                if((laser.leste - laser.oeste) >= 0.4):
                    print('\t\t\tCorrigindo pra direita...')
                    tipoMovimento = virarDireita
            elif(laser.oeste > laser.leste and laser.noroeste >= 0.5): #mais espaço na esquerda
                if((laser.oeste - laser.leste) >= 0.4):
                    print('\t\t\tCorrigindo pra esquerda...')
                    tipoMovimento = virarEsquerda


        print('teste:', str(laser.msg.ranges[5]))
        print('tratouPerigo:', tratouPerigo)
        print('tipoMovimento:', tipoMovimento)
        print('contLoop:', contLoop)
        print('ehCurva:', ehCurva)
        print('loopRestCurva: ', loopRestCurva)

        # corrige bug de indecisão em cantos cuja única opção é virar 180 e voltar
        if(tratouPerigo and (ultimoMov != 1) and 
            (ultimoMov != andarEsquerda) and 
            (ultimoMov != andarDireita) and 
            (tipoMovimento != ultimoMov)):
            print('Corrigiu!')
            tipoMovimento = ultimoMov

        ultimoMov = tipoMovimento
        contLoop += 1
        
        #if(laser.oeste <= 0.1 or laser.leste <= 0.1 or laser.norte <= 0.1):
            #tipoMovimento = re

        if(ehCurva != 0):
            if(loopRestCurva > 0):
                tipoMovimento = ehCurva
                loopRestCurva -= 1
            else:
                ehCurva = 0

        if(laser.oeste == math.inf and laser.noroeste == math.inf and laser.nornoroeste == math.inf
            and laser.norte == math.inf and laser.nornordeste == math.inf and laser.nordeste == math.inf
            and laser.leste == math.inf):
            tipoMovimento = parar

        velocidade.movimenta(tipoMovimento)

        if((contLoop % 3) == 0):
            ultimoNoroeste = laser.noroeste
            ultimoNordeste = laser.nordeste
        
        # if( (laser.norte < 0.4 and laser.norte != 0.0) or
        #     (laser.noroeste < 0.5 and laser.noroeste != 0.0) or 
        #     (laser.nordeste < 0.4 and laser.nordeste != 0.0)):
        #     tem_parede = 1
        #     print("Distância da parede: ", str(laser.norte))
        #     print("com parede à frente")
        # else:
        #     tem_parede = 0
        #     print("sem parede à frente")

        #velocidade.movimenta(tem_parede)
            
if __name__ == '__main__':
    main()
