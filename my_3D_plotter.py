
"""
my pyglet based 3D plotter
press p to see the info and input page
use the mouse to move the frame or keys qwerasdf
can take multiple equations at a time on the same axis
can also do a scatter plot - import the data from a file called datalist.txt
smoother rendering than with pygame
"""
"""
Using:
Python 3.6.6
Pyglet 1.3.3
"""

from math import *     # use this in eval(eq)
import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse, FPSDisplay

# Base sizes
u = 50  # The length of an axis of the plot frame is 2*u
g = 1   # The resolution of the equation calculation for rendering

vertices = [
    u, 0, u,
    -u, 0, u,
    -u, 0, -u,
    u, 0, -u,
    0, u, u,
    0, u, -u,
    0, -u, -u,
    0, -u, u,
    u, u, 0,
    -u, u, 0,
    -u, -u, 0,
    u, -u, 0,
    0, 0, 0,
    0, 0, u,
    -u, 0, 0,
    0, 0, -u,
    u, 0, 0,
    0, u, 0,
    0, -u, 0
]

# Define the list of colors to be used in the plots
colors =[[0, 255, 255],
        [255, 255, 0],
        [255, 0, 255],
        [255, 0, 0],
        [0, 255, 0],
        [0, 0, 255]]


class Equation:
    def __init__(self, equation, color, u, g, main_batch):
        self.indices = [0,1,0,2]
        eq = equation

        for i in range(-u, u, g):
            for j in range(-u, u, g):
                self.nodes = []
                x = i
                z = j
                y = eval(eq)
                point1 = [x,y,z]
                x = i+g
                z = j
                y = eval(eq)
                point2 = [x,y,z]
                x = i
                z = j+g
                y = eval(eq)
                point3 = [x,y,z]

                self.nodes.extend(point1)
                self.nodes.extend(point2)
                self.nodes.extend(point3)
                main_batch.add_indexed(3, pyglet.gl.GL_LINES, None, self.indices,
                                      ('v3f', self.nodes),
                                      ('c3B', color * 3))


class ScatterPlot:
    def __init__(self, data):
        self.number = len(data)//3
        self.points = data
        self.vertices = pyglet.graphics.vertex_list(self.number,
                                                 ('v3f', self.points),
                                                 ( 'c3B',
                                                    [255,100,100] * self.number
                                                      ))


class Marker:
    # Color the x,y,z axis ends with r g b points
    def __init__(self, u):
        self.vertices = pyglet.graphics.vertex_list(3,
                                                 ('v3f', [u, 0.0, 0.0,
                                                         0.0, u, 0.0,
                                                         0.0, 0.0, u,
                                                         ]),
                                                 ('c3B', [255, 0, 0,
                                                         0, 255, 0,
                                                         0, 0, 255] ))


class Frame:
    # Draws the main frame of the axis
    def __init__(self, vertex_lst):
        self.vertices = vertex_lst
        self.indices = [0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4,
                        8, 9, 9, 10, 10, 11, 11, 8, 13, 15, 14, 16, 17, 18]
        self.vertices = pyglet.graphics.vertex_list_indexed(19, self.indices,('v3f', self.vertices))


class Grid:
    # Draws a grid on each axis
    def __init__(self, u):
        k = u // 10
        self.nodes = []
        self.number = 12 * ((2 * u) // k)
        for i in range(int(2 * u // k)):
            gridx = k * i
            grid_points = [u - gridx, 0, u, u - gridx, 0, -u,
                           -u, 0, u - gridx, u, 0, u - gridx,
                           0, u, -u + gridx, 0, -u, -u + gridx,
                           0, -u + gridx, u, 0, -u + gridx, -u,
                           -u + gridx, u, 0, -u + gridx, -u, 0,
                           -u, u - gridx, 0, u, u - gridx, 0
                           ]
            self.nodes.extend(grid_points)
        self.vertices = pyglet.graphics.vertex_list(self.number,('v3f', self.nodes))


class GreetWindow(pyglet.window.Window):
    def __init__(self, window_x,  window_y, *args, **kwargs):
        super().__init__(*args, **kwargs)
        glClearColor(0.5, 0.7, 0.8, 1.0)
        self.frame_rate = 1 / 60
        self.rotate_axis = 0
        pyglet.clock.schedule_interval(self.update, self.frame_rate)
        pyglet.window.Window.switch_to(self)  # moves the OpenGL instance to this window
        self.set_size(800, 600)
        self.set_caption('Greeting Window')
        self.greeting = pyglet.graphics.Batch()

        self.label1 = pyglet.text.Label(
                            "Henko's Amazing Flying 3D Plotter" ,
                                   font_name='Arial',
                                   font_size=24,
                                   x=30,
                                   y=550,
                                   anchor_x='left',
                                   anchor_y='bottom', batch=self.greeting)

        self.label2 = pyglet.text.Label(
                            'Use the mouse to move the frame, or keys q w e r a s d f, '
                            'or the arrow keys.',
                                    font_name='Arial',
                                    font_size=16,
                                    x=30,
                                    y=520,
                                    anchor_x='left',
                                    anchor_y='bottom', batch=self.greeting)

        self.label3 = pyglet.text.Label(
                            'Press p to see the equation input page.',
                                    font_name='Arial',
                                    font_size=16,
                                    x=30,
                                    y=490,
                                    anchor_x='left',
                                    anchor_y='bottom', batch=self.greeting)

        self.label4 = pyglet.text.Label(
                            'The plotter can display the plots of up to 6 '
                            'equations at a time.',
                                    font_name='Arial',
                                    font_size=16,
                                    x=30,
                                    y=460,
                                    anchor_x='left',
                                    anchor_y='bottom', batch=self.greeting)

        self.label5 = pyglet.text.Label(
                                    'Press Enter to start or p to enter your equation.',
                                    font_name='Arial',
                                    font_size=16,
                                    color=(255,255,255,255),
                                    x=30,
                                    y=430,
                                    anchor_x='left',
                                    anchor_y='bottom', batch=self.greeting)

    def on_key_press(self, symbol, modifiers):  # input handler
        if symbol == key.ESCAPE:  # closes the whole  app - Escape!
            pyglet.app.exit()

        if symbol == key.RETURN:
            window.rotate_axis = 1
            window.active = 1
            self.close()

        if symbol == key.P:
            # opens the text input panel
            text_panel = TextWindow(100, 100, vsync=True)
            text_panel.set_location(100, 150)
            self.close()

    def on_close(self):  # using the x in the window corner
        window.rotate_axis = 1
        self.close()

    def on_draw(self):
        glClear((GL_COLOR_BUFFER_BIT))
        self.greeting.draw()

    def update(self, dt):
        self.on_draw()


class TextWindow(pyglet.window.Window):
    def __init__(self, window_x,  window_y, *args, **kwargs):
        super().__init__(*args, **kwargs)
        glClearColor(0.6, 0.7, 0.7, 1.0)
        self.frame_rate = 1 / 60
        pyglet.clock.schedule_interval(self.update, self.frame_rate)
        pyglet.window.Window.switch_to(self)  # moves the OpenGL instance to this window
        self.set_size(1200, 700)
        self.set_caption('Text Input Window')
        self.instructions = pyglet.graphics.Batch()
        self.second_plot = True   # to show the eq of other running plots
        self.color_rotate = [0, 1, 2, 3, 4, 5]
        # self.update_text()
        self.label1 = pyglet.text.Label(
                            "Henko's Amazing Flying 3D Plotter" ,
                                   font_name='Arial',
                                   font_size=24,
                                   x=30,
                                   y=650,
                                   anchor_x='left',
                                   anchor_y='bottom', batch=self.instructions)

        self.label2 = pyglet.text.Label(
                            'Type in an equation with x and z values: eg. -3*x^2-3*z-2',
                                    font_name='Arial',
                                    font_size=16,
                                    x=30,
                                    y=620,
                                    anchor_x='left',
                                    anchor_y='bottom', batch=self.instructions)

        self.label3 = pyglet.text.Label(
                            'Select "Enter" when done or "q" to start over.',
                                    font_name='Arial',
                                    font_size=16,
                                    x=30,
                                    y=590,
                                    anchor_x='left',
                                    anchor_y='bottom', batch=self.instructions)

        self.label4 = pyglet.text.Label(
                            'Select "backspace" to clear.',
                                    font_name='Arial',
                                    font_size=16,
                                    x=30,
                                    y=560,
                                    anchor_x='left',
                                    anchor_y='bottom', batch=self.instructions)

        self.label5 = pyglet.text.Label(
            's=sin(), c=cos(), t=tan(), r=sqrt, a=abs(), l=log10(), n=log()',
                                    font_name='Arial',
                                    font_size=16,
                                    color=(255,255,255,255),
                                    x=30,
                                    y=530,
                                    anchor_x='left',
                                    anchor_y='bottom', batch=self.instructions)
        self.label6 = pyglet.text.Label(
                                    'e=e, p=pi ',
                                    font_name='Arial',
                                    font_size=16,
                                    x=30,
                                    y=510,
                                    anchor_x='left',
                                    anchor_y='bottom', batch=self.instructions)

        self.label7 = pyglet.text.Label(
            'Press G for another plot on the same axis',
            font_name='Arial',
            font_size=16,
            x=60,
            y=300,
            anchor_x='left',
            anchor_y='bottom', batch=self.instructions)

        self.label8 = pyglet.text.Label(
            'Other running functions:',
            font_name='Arial',
            font_size=16,
            x=80,
            y=270,
            anchor_x='left',
            anchor_y='bottom', batch=self.instructions)

    def update_text(self):  # updating the dynamic text
        self.eq = ''.join(str(e) for e in window.equation)     # new equation being entered
        self.label10 = pyglet.text.Label('Function: y = '+ self.eq,
                                           font_name='Arial',
                                           font_size=20,
                                           x=80,
                                           y=340,
                                           anchor_x='left',
                                           anchor_y='bottom')

    def write_equations(self,index):   # write the equations being rendered
        eq = ''.join(str(e) for e in window.eq_list[-index])
        if eq != '':
            self.label = pyglet.text.Label('Function: y = ' + eq,
                                           font_name='Arial',
                                           font_size=15,
                                           x=200,
                                           y=270 - (index * 30),
                                           anchor_x='left',
                                           anchor_y='bottom')

    def on_key_press(self, symbol, modifiers):  # input handler
        if symbol == key.ESCAPE:  # closes the whole  app - Escape!
            pyglet.app.exit()

        if symbol == key.RETURN:
            c = window.color_rotate.pop(0)
            window.color_rotate.append(c)
            window.rotate_axis = 1
            window.active = 1
            render_equation(self.eq, colors[c])
            self.close()

        if symbol == key._1:
            window.equation.append('1')
        elif symbol == key._2:
            window.equation.append('2')
        elif symbol == key._3:
            window.equation.append('3')
        elif symbol == key._4:
            window.equation.append('4')
        elif symbol == key._5:
            window.equation.append('5')
        elif symbol == key._6:
            window.equation.append('6')
        elif symbol == key._7:
            window.equation.append('7')
        elif symbol == key._8:
            window.equation.append('8')
        elif symbol == key._9:
            window.equation.append('9')
        elif symbol == key._0:
            window.equation.append('0')
        elif symbol == key.ASTERISK:
            window.equation.append('*')
        elif symbol == key.PLUS:
            window.equation.append('+')
        elif symbol == key.MINUS:
            window.equation.append('-')
        elif symbol == key.SLASH:
            window.equation.append('/')
        elif symbol == key.PERIOD:
            window.equation.append('.')
        elif symbol == key.PARENLEFT:
            window.equation.append('(')
        elif symbol == key.PARENRIGHT:
            window.equation.append(')')
        elif symbol == key.ASCIICIRCUM:
            window.equation.append('**')

        elif symbol == key.Z:
            window.equation.append('z')
        elif symbol == key.X:
            window.equation.append('x')
        elif symbol == key.Q:
            window.equation = []
            window.eq_list = []

        elif symbol == key.C:
            window.equation.append('cos(')
        elif symbol == key.S:
            window.equation.append('sin(')
        elif symbol == key.T:
            window.equation.append('tan(')
        elif symbol == key.R:
            window.equation.append('sqrt(')
        elif symbol == key.A:
            window.equation.append('abs(')
        elif symbol == key.L:
            window.equation.append('log10(')
        elif symbol == key.N:
            window.equation.append('log(')
        elif symbol == key.E:
            window.equation.append('e')
        elif symbol == key.P:
            window.equation.append('pi')

        elif symbol == key.G:
            self.second_plot = True
            window.eq_list.append(window.equation)
            window.equation = []

        elif symbol == key.BACKSPACE:
            try:            # use try in case the equation list is empty
                window.equation.pop()
            except:
                pass

    def on_close(self):  # using the x in the window corner
        window.rotate_axis = 1
        self.close()

    def on_draw(self):
        glClear((GL_COLOR_BUFFER_BIT))
        self.label10.draw()
        self.instructions.draw()
        if self.second_plot:
            try:    # try in case the eq_list is empty
                eq_len = len(window.eq_list)
                for i in range(1, eq_len + 1, 1):
                    self.write_equations(i)
                    self.label.draw()
            except:
                pass

    def update(self, dt):
        self.update_text()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, 1200, 0, 700, -10,10)
        glMatrixMode(GL_MODELVIEW)


def render_equation(equation, color):
    if len(equation) != 0 and window.active:
        try:
            Equation(equation, color, window.u, window.g, window.main_batch)
        except:
            print('Cannot render this equation')


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(200, 100)
        self.frame_rate = 1 / 60
        self.fps_display = FPSDisplay(self)
        self.main_batch = pyglet.graphics.Batch()
        pyglet.clock.schedule_interval(self.update, self.frame_rate)
        pyglet.window.Window.switch_to(self)
        self.u = u
        self.g = g
        glClearColor(0.6, 0.7, 0.7, 1.0)
        gluPerspective(45.0, (1200 / 700), 1, -100.0)
        glTranslatef(0.0, 0.0, -(4*self.u))
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_DEPTH_TEST)
        glLineWidth(4)
        self.frame = Frame(vertices)
        glLineWidth(1)
        self.window_x = 10
        self.window_y = 10
        self.grid = Grid(self.u)
        self.marker = Marker(self.u)
        self.color_rotate = [0, 1, 2, 3, 4, 5]
        # read the text data file
        data_file = open('res/datalist.txt')
        content = data_file.readline()
        data_file.close()
        # strip and split the file and turn it into a list of integers
        datalist = [int(x) for x in content.strip().split(',')]
        # plot the data
        self.scatter_plot = scatter
        self.scatter = ScatterPlot(datalist)

        # self.rotate_axis = 1
        self.equation = []
        self.eq_list = []
        self.active = 0
        self.eq = ''
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.forward = False
        self.backward = False
        self.rotatexp = False
        self.rotatexn = False
        self.rotateyp = False
        self.rotateyn = False
        self.rotatezp = False
        self.rotatezn = False
        self.x_rot = 0
        self.y_rot = 0
        self.move = 10  # set the base translation speed

        # start with the greeting panel
        self.rotate_axis = 0
        greet_panel = GreetWindow(100, 100, vsync=True)
        greet_panel.set_location(100, 150)


    def on_key_press(self, symbol, modifiers):  # input handler
        if symbol == key.ESCAPE:
            # exits the app
            pyglet.app.exit()

        if symbol == key.P:
            self.rotate_axis = 0
            # opens the text input panel
            text_panel = TextWindow(100, 100, vsync=True)
            text_panel.set_location(self.window_x, self.window_y - 28)

        if symbol == key.RIGHT:
            self.right = True
        if symbol == key.LEFT:
            self.left = True
        if symbol == key.UP:
            self.up = True
        if symbol == key.DOWN:
            self.down = True
        if symbol == key.Q:
            self.forward = True
        if symbol == key.A:
            self.backward = True

        if symbol == key.W:
            self.rotatexp = True
        if symbol == key.S:
            self.rotatexn = True
        if symbol == key.E:
            self.rotateyp = True
        if symbol == key.D:
            self.rotateyn = True
        if symbol == key.R:
            self.rotatezp = True
        if symbol == key.F:
            self.rotatezn = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.RIGHT:
            self.right = False
        if symbol == key.LEFT:
            self.left = False
        if symbol == key.UP:
            self.up = False
        if symbol == key.DOWN:
            self.down = False
        if symbol == key.Q:
            self.forward = False
        if symbol == key.A:
            self.backward = False

        if symbol == key.W:
            self.rotatexp = False
        if symbol == key.S:
            self.rotatexn = False
        if symbol == key.E:
            self.rotateyp = False
        if symbol == key.D:
            self.rotateyn = False
        if symbol == key.R:
            self.rotatezp = False
        if symbol == key.F:
            self.rotatezn = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            self.y_rot = dx / 5
            self.x_rot = -dy / 5

        glRotatef(self.x_rot, 1, 0, 0)
        glRotatef(self.y_rot, 0, 1, 0)

    def update_rotate(self):
        q, w, e = 0, 0, 0
        if self.rotatexp == True:
            q = 1
        if self.rotatexn == True:
            q = -1
        if self.rotatexp == False and self.rotatexn == False:
            q = 0.0
        if self.rotateyp == True:
            w = 1
        if self.rotateyn == True:
            w = -1
        if self.rotateyp == False and self.rotateyn == False:
            w = 0
        if self.rotatezp == True:
            e = -1
        if self.rotatezn == True:
            e = 1
        if self.rotatezp == False and self.rotatezn == False:
            e = 0
        return q, w, e

    def update_translate(self):
        r, t, y = 0, 0, 0
        if self.right == True:
            r = 1
        if self.left == True:
            r = -1
        if self.right == False and self.left == False:
            r = 0.0
        if self.up == True:
            t = 1
        if self.down == True:
            t = -1
        if self.up == False and self.down == False:
            t = 0
        if self.forward == True:
            y = -1
        if self.backward == True:
            y = 1
        if self.forward == False and self.backward == False:
            y = 0
        return r, t, y

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.z_trans = scroll_y
        glTranslatef(0, 0, self.z_trans)

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPointSize(5)    # size of the plot points
        if self.scatter_plot ==1:
            self.scatter.vertices.draw(GL_POINTS)  # to show the scatter plot
        glLineWidth(4)
        self.frame.vertices.draw(GL_LINES)
        glLineWidth(1)
        self.grid.vertices.draw(GL_LINES)
        glPointSize(10)   # size of the axis color points
        self.marker.vertices.draw(GL_POINTS)
        self.main_batch.draw()
        self.fps_display.draw()

    def update(self, dt):
        q, w, e = self.update_rotate()
        r, t, y = self.update_translate()
        glTranslatef(self.move*r*dt, self.move*t*dt, self.move*y*dt)
        glRotatef(dt*30, q, w, e)
        self.window_x, self.window_y = self.get_location()
        if rotate == 1:
            glRotatef(dt * 15, self.rotate_axis, self.rotate_axis, 0)  # to rotate by itself

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)


if __name__ == '__main__':
    scatter_plot = input('Do you want to run the scatter plot? y/n\n:')
    if scatter_plot == 'y':
        scatter = 1
    else:
        scatter = 0
    auto_rotate = input('Do you want the frame to auto rotate? y/n\n:')
    if auto_rotate == 'y':
        rotate = 1
    else:
        rotate = 0
    window = MyWindow(1400, 800, 'My Window', resizable=False, vsync=False)
    pyglet.app.run()
