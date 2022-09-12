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
        #self.timer = self.create_timer(timer_period, self.movimenta)
        self.vel_msg = Twist()
        self.vel_msg.linear.x = 0.0  
        self.vel_msg.linear.y = 0.0 
        self.vel_msg.linear.z = 0.0  
        self.vel_msg.angular.x = 0.0
        self.vel_msg.angular.y = 0.0  
        self.vel_msg.angular.z = 0.0

def main(args=None):
    rclpy.init(args=args)

    #subscreve ao leiser e ao publiser de movimentos
    laser = LaserSub()
    velocidade = VelocidadePub()

    command = Twist()
    command.linear.x = 0.0
    command.angular.z = 0.0

    proximo_parede = 0 #muda para 1 quando localizar a primeira parede na esquerda

    print("Virando...")
    command.angular.z = -0.1
    command.linear.x = 0.1
    velocidade.velocity_publisher.publish(command)

    range_front = []
    range_right = []
    range_left  = []
    minimo_frente = 0
    minimo_direita = 0
    minimo_esquerda = 0
    i_front = 0
    i_right = 0
    i_left = 0

    contLoop = 0
    cont = 0

    while(True):
        rclpy.spin_once(laser)
        print('contLoop', contLoop)

        msg = laser.msg
        ranges = msg.ranges
        # calcula a frente do robo do grau -5 até 5
        range_front[:5] = msg.ranges[5:0:-1]  
        range_front[5:] = msg.ranges[-1:-5:-1]
        # na direita entre 300 e 345 graus
        range_right = msg.ranges[300:345]
        # na esquerda entre 15 e 60 graus
        range_left = msg.ranges[60:15:-1]
        # pega os menores valores em cada direção
        min_range,i_range = min( (ranges[i_range],i_range) for i_range in range(len(ranges)) )
        minimo_frente,i_front = min( (range_front[i_front],i_front) for i_front in range(len(range_front)) )
        minimo_direita,i_right = min( (range_right[i_right],i_right) for i_right in range(len(range_right)) )
        minimo_esquerda,i_left  = min( (range_left [i_left ],i_left ) for i_left  in range(len(range_left )) )

        print('minimo_esquerda: ' + str(round(minimo_esquerda,3)) + ' - minimo_frente: ' + str(round(minimo_frente,3)) + ' - minimo_direita: ' + str(round(minimo_direita,3)))

        # detecta a parede da esquerda mais próxima 
        while(proximo_parede == 0):
            rclpy.spin_once(laser)

            msg = laser.msg
            ranges = msg.ranges
            # calcula a frente do robo do grau -5 até 5
            range_front[:5] = msg.ranges[5:0:-1]  
            range_front[5:] = msg.ranges[-1:-5:-1]
            # na direita entre 300 e 345 graus
            range_right = msg.ranges[300:345]
            # na esquerda entre 15 e 60 graus
            range_left = msg.ranges[60:15:-1]
            # pega os menores valores em cada direção
            min_range,i_range = min( (ranges[i_range],i_range) for i_range in range(len(ranges)) )
            minimo_frente,i_front = min( (range_front[i_front],i_front) for i_front in range(len(range_front)) )
            minimo_esquerda,i_right = min( (range_right[i_right],i_right) for i_right in range(len(range_right)) )
            minimo_direita,i_left  = min( (range_left [i_left ],i_left ) for i_left  in range(len(range_left )) )

            print('minimo_esquerda: ' + str(round(minimo_esquerda,3)) + ' - minimo_frente: ' + str(round(minimo_frente,3)) + ' - minimo_direita: ' + str(round(minimo_direita,3)))

            print('Movendo em direção a parede...')
            if(minimo_frente > 0.2 and minimo_direita > 0.2 and minimo_esquerda > 0.2):    
                command.angular.z = -0.1    # if nothing near, go forward
                command.linear.x = 0.1
                print("Seguindo reto...")
            elif(minimo_esquerda < 0.2): # if wall on left, start tracking
                proximo_parede = 1       
                print("Tracking...")            
            else:
                print('virando esquerda')
                command.angular.z = 0.25   # if not on left, turn right 
                command.linear.x = 0.0

            velocidade.velocity_publisher.publish(command)

        if(minimo_frente > 0.22):
            if(minimo_esquerda < 0.135):
                print("Range: {:.2f}m - Muito próximo. Dando ré.".format(minimo_esquerda))
                command.angular.z = -0.2
                command.linear.x = -0.1
                cont = 0
            elif(minimo_esquerda < 0.15):
                print("Range: {:.2f}m - Muito próximo. Virando direita.".format(minimo_esquerda))
                command.angular.z = -0.2
                command.linear.x = 0.0
                cont = 0
            elif(minimo_esquerda > 0.3):
                print('cont', cont)
                if(cont > 5):
                    print("Range: {:.2f}m - Seguindo parede; virando pra esquerda (rápido).".format(minimo_esquerda))
                    command.angular.z = 0.4
                    command.linear.x = 0.0
                cont += 1
            elif(minimo_esquerda > 0.22):
                print("Range: {:.2f}m - Seguindo parede; virando pra esquerda.".format(minimo_esquerda))
                command.angular.z = 0.2
                command.linear.x = 0.1
                cont = 0
            else:
                print("Range: {:.2f}m - Seguindo parede; virando pra direita.".format(minimo_esquerda))
                command.angular.z = -0.2
                command.linear.x = 0.1
                cont = 0
        else:
            print("Detectou obstaculo na frente. Virando pra direita...")
            command.angular.z = -0.2
            command.linear.x = 0.0
            velocidade.velocity_publisher.publish(command)
            while(minimo_frente < 0.3):
                rclpy.spin_once(laser)

                msg = laser.msg
                ranges = msg.ranges
                # calcula a frente do robo do grau -5 até 5
                range_front[:5] = msg.ranges[5:0:-1]  
                range_front[5:] = msg.ranges[-1:-5:-1]
                # na direita entre 300 e 345 graus
                range_right = msg.ranges[300:345]
                # na esquerda entre 15 e 60 graus
                range_left = msg.ranges[60:15:-1]
                # pega os menores valores em cada direção
                min_range,i_range = min( (ranges[i_range],i_range) for i_range in range(len(ranges)) )
                minimo_frente,i_front = min( (range_front[i_front],i_front) for i_front in range(len(range_front)) )
                minimo_direita,i_right = min( (range_right[i_right],i_right) for i_right in range(len(range_right)) )
                minimo_esquerda ,i_left  = min( (range_left [i_left ],i_left ) for i_left  in range(len(range_left )) )      
                pass

        velocidade.velocity_publisher.publish(command)

        contLoop += 1
            
if __name__ == '__main__':
    main()
