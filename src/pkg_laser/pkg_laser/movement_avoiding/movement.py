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
        self.get_logger().info('criou publisher!!')

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

    def para(self):
        move_cmd = Twist()
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 0.0

        print(self.velocity_publisher)
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



def main(args=None):
    rclpy.init(args=args)

    laser = LaserSub()
    velocidade = VelocidadePub()

    ultimoMov = 1
    contLoop = 0
    contFrente = 0

    ultimoNoroeste = -1.0
    ultimoNordeste = -1.0

    while(True):
        rclpy.spin_once(laser)
        
        andarEsquerda = 2
        andarDireita = 3
        virarEsquerda = 4
        virarDireita = 5
        re = 6
        rodar90graus = 7

        tipoMovimento = 1 #andar pra frente

        seguroOeste = (laser.oeste > 0.10 and laser.oeste != 0.0) or laser.oeste == math.inf
        seguroNoroeste = (laser.noroeste > 0.25 and laser.noroeste != 0.0) or laser.noroeste == math.inf
        seguroNorNoroeste = (laser.nornoroeste > 0.27 and laser.nornoroeste != 0.0) or laser.nornoroeste == math.inf
        seguroNorte = (laser.norte > 0.3 and laser.norte != 0.0) or laser.norte == math.inf
        seguroNorNordeste = (laser.nornordeste > 0.27 and laser.nornordeste != 0.0) or laser.nornordeste == math.inf
        seguroNordeste = (laser.nordeste > 0.25 and laser.nordeste != 0.0) or laser.nordeste == math.inf
        seguroLeste = (laser.leste > 0.10 and laser.leste != 0.0) or laser.leste == math.inf
        
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
        if(seguroNorte == False):
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
                        tipoMovimento = virarEsquerda
                    else:
                        tipoMovimento = virarDireita
                else:
                    tipoMovimento = virarEsquerda
            else:
                tipoMovimento = virarDireita
            
            tratouPerigo = True
        elif(seguroNoroeste == False):
            tipoMovimento = virarDireita
            tratouPerigo = True
        elif(seguroNordeste == False):
            tipoMovimento = virarEsquerda
            tratouPerigo = True
        elif(seguroNorNoroeste == False):
            tipoMovimento = virarDireita
            tratouPerigo = True
        elif(seguroNorNordeste == False):
            tipoMovimento = virarEsquerda
            tratouPerigo = True

        if(tipoMovimento == 1 and (contLoop % 3) == 0):
            print('corrigindo...')
            # if((ultimoNoroeste - laser.noroeste) >= 0.04):
            #     tipoMovimento = virarDireita
            # elif((ultimoNordeste - laser.nordeste) >= 0.04):
            #     tipoMovimento = virarEsquerda
            if(laser.leste > laser.oeste and laser.nordeste >= 0.5): #mais espaço na direita
                if((laser.leste - laser.oeste) >= 0.4):
                    print('\t\t\tCorrigindo pra direita...')
                    tipoMovimento = virarDireita
            elif(laser.oeste > laser.leste and laser.noroeste >= 0.5): #mais espaço na esquerda
                if((laser.oeste - laser.leste) >= 0.4):
                    print('\t\t\tCorrigindo pra esquerda...')
                    tipoMovimento = virarEsquerda

        #dificuldade em encontrar cantos
        # if((ultimoNoroeste - laser.noroeste) >= 0.05 and laser.norte > 0.8):
        #     print('\t\t Tratamento de beira de parede...')
        #     tipoMovimento = virarDireita

        # if(tratouPerigo == False and seguroLeste == False):
        #     tipoMovimento = virarEsquerda
        #     tratouPerigo = True
        # if(tratouPerigo == False and seguroOeste == False):
        #     tipoMovimento = virarDireita
        #     tratouPerigo = True

        print('tratouPerigo:', tratouPerigo)
        print('tipoMovimento:', tipoMovimento)
        print('contLoop:', contLoop)
        if(tratouPerigo and (ultimoMov != 1) and 
            (ultimoMov != andarEsquerda) and 
            (ultimoMov != andarDireita) and 
            (tipoMovimento != ultimoMov)):
            print('Corrigiu!')
            tipoMovimento = ultimoMov

        ultimoMov = tipoMovimento
        contLoop += 1
        if(tipoMovimento == 1):
            contFrente += 1
        else:
            contFrente = 0

        # if(contFrente == 5):
        #     tipoMovimento = 5
        if(laser.oeste <= 0.1 or laser.leste <= 0.15 or laser.norte <= 0.15):
            tipoMovimento = re

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
