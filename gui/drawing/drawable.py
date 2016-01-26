# -*- coding: utf-8 -*-

import abc
import cairo

from gi.repository import Gtk

from enum import Enum

from drawing.geometry import Margin, RectangleBBox
from drawing.size import Size
from drawing.vector import Vector
from enums import TypeCategory
from events import EventBroadcaster
from mouse import ClickHandler


class FontStyle(object):
    def __init__(self, color=None, bold=False, italic=False, font_family=None):
        """
        Represents style of a font.
        @type color: Color
        @type bold: bool
        @type italic: bool
        @type font_family: basestring
        """
        if not color:
            color = Color()

        self.color = color
        self.bold = bold
        self.italic = italic
        self.font_family = font_family


class Color(object):
    def __init__(self, red=0.0, green=0.0, blue=0.0, alpha=1.0):
        """
        Represents RGBA color.
        @type red: float
        @type green: float
        @type blue: float
        @type alpha: float
        """
        self._red = red
        self._green = green
        self._blue = blue
        self._alpha = alpha

    @property
    def red(self):
        return self._red

    @property
    def green(self):
        return self._green

    @property
    def blue(self):
        return self._blue

    @property
    def alpha(self):
        return self._alpha


class DrawingUtils(object):
    @staticmethod
    def apply_font_style(canvas, font_style):
        """
        Applies the given font style to the given canvas.
        @type canvas: canvas.Canvas
        @type font_style: FontStyle
        """
        canvas.cr.select_font_face(font_style.font_family if font_style.font_family else "sans-serif",
                            cairo.FONT_SLANT_ITALIC if font_style.italic else cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD if font_style.bold else cairo.FONT_WEIGHT_NORMAL)

    @staticmethod
    def get_text_size(canvas, text, font_style=None):
        """
        @type canvas: canvas.Canvas
        @type text: basestring
        @type font_style: FontStyle
        """
        if not font_style:
            font_style = FontStyle()

        canvas.cr.save()

        DrawingUtils.apply_font_style(canvas, font_style)
        size = canvas.cr.text_extents(text)

        size = Size(size[2], -size[1])   # (width, height)

        canvas.cr.restore()

        return size

    @staticmethod
    def set_color(canvas, color):
        """
        Sets color for Cairo context in canvas.
        @type canvas: canvas.Canvas
        @type color: Color
        """
        canvas.cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)

    @staticmethod
    def draw_text(canvas, text, position, y_center=False, x_center=False, font_style=None):
        """
        Draws text on a given position. When no centering is set, it will be drawn from top-left corner.
        @type canvas: canvas.Canvas
        @type text: str
        @type position: Vector
        @type y_center: bool
        @type x_center: bool
        @type font_style: FontStyle
        """
        if not font_style:
            font_style = FontStyle()

        cr = canvas.cr
        cr.save()

        DrawingUtils.apply_font_style(canvas, font_style)

        position = Vector.vectorize(position)

        text = text.strip()
        text_size = DrawingUtils.get_text_size(canvas, text)

        if x_center:
            position.x -= text_size.width / 2.0

        if y_center:
            w_size = DrawingUtils.get_text_size(canvas, "W")
            position.y += w_size.height / 2.0
        else:
            position.y += text_size.height

        DrawingUtils.set_color(canvas, font_style.color)
        cr.move_to(position.x, position.y)

        cr.show_text(text)

        cr.restore()

    @staticmethod
    def draw_line(canvas, point_from, point_to, color=Color(), width=1.0):
        """
        @type canvas: drawing.canvas.Canvas
        @type point_from: drawing.vector.Vector
        @type point_to: drawing.vector.Vector
        @type color: Color
        @type width: float
        """
        cr = canvas.cr
        cr.save()

        point_from = Vector.vectorize(point_from)
        point_to = Vector.vectorize(point_to)

        DrawingUtils.set_color(canvas, color)
        cr.set_line_width(width)

        cr.move_to(point_from.x, point_from.y)
        cr.line_to(point_to.x, point_to.y)
        cr.stroke()

        cr.restore()

    @staticmethod
    def draw_arrow(canvas, point_from, point_to, color=Color(), width=1):
        """
        @type canvas: drawing.canvas.Canvas
        @type point_from: vector.Vector
        @type point_to: vector.Vector
        @type color: Color
        @type width: float
        """
        point_from = Vector.vectorize(point_from)
        point_to = Vector.vectorize(point_to)

        DrawingUtils.draw_line(canvas, point_from, point_to, color, width)

        vec_arrow = point_to.sub(point_from)

        wing = vec_arrow.inverse().normalized().scaled(10)
        wing_right = wing.copy().rotate(45)
        wing_left = wing.copy().rotate(-45)

        DrawingUtils.draw_line(canvas, point_to, wing_right.add(point_to).to_point(), color, width)
        DrawingUtils.draw_line(canvas, point_to, wing_left.add(point_to).to_point(), color, width)

    @staticmethod
    def draw_arrow_path(canvas, path, color=Color(), width=1):
        """
        @type canvas: drawing.canvas.Canvas
        @type path: list of (drawing.vector.Vector)
        @type color: Color
        @type width: float
        """
        if len(path) < 2:
            return

        point_from = path[0]

        for index, point in enumerate(path):
            point_to = point

            if index == len(path) - 1:  # draw arrow
                DrawingUtils.draw_arrow(canvas, point_from, point_to, color, width)
            else:  # draw connecting line
                DrawingUtils.draw_line(canvas, point_from, point_to, color, width)

            point_from = point_to

    @staticmethod
    def draw_rectangle(canvas, position, size, color=Color(), width=1, center=False):
        cr = canvas.cr
        cr.save()

        position = Vector.vectorize(position)
        size = Size.make_size(size)

        if center:
            position.x -= size.width / 2
            position.y -= size.height / 2

        DrawingUtils.set_color(canvas, color)
        cr.set_line_width(width)
        cr.rectangle(position.x, position.y, size.width, size.height)
        cr.stroke()

        cr.restore()

    @staticmethod
    def draw_image(canvas, position, img_path, size=None, center=False):
        """
        Draws an image given by a file path.
        @type canvas: canvas.Canvas
        @type position: vector.Vector
        @type img_path: basestring
        @type size: size.Size
        @type center: boolean
        """
        img = cairo.ImageSurface.create_from_png(img_path)
        DrawingUtils.draw_image_from_surface(canvas, position, img, size, center)

    @staticmethod
    def draw_image_from_surface(canvas, position, img, size=None, center=False):
        """
        Draws an image given by a cairo.ImageSurface object.
        @type canvas: canvas.Canvas
        @type position: vector.Vector
        @type img: cairo.ImageSurface
        @type size: size.Size
        @type center: boolean
        """
        if not size:
            size = Size(img.get_width(), img.get_height())
        else:
            size = Size.make_size(size)

        position = Vector.vectorize(position)
        width = img.get_width()
        height = img.get_height()

        cr = canvas.cr

        cr.save()

        if center:
            cr.translate(position.x - size.width / 2.0, position.y - size.height / 2.0)
        else:
            cr.translate(position.x, position.y)

        x_ratio = float(size.width) / width
        y_ratio = float(size.height) / height
        cr.scale(x_ratio, y_ratio)

        cr.set_source_surface(img)
        cr.get_source().set_filter(cairo.FILTER_FAST)
        cr.paint()

        cr.restore()


class ValueEntry(Gtk.Frame):
    def __init__(self, label):
        """
        @type label: basestring
        """
        Gtk.Frame.__init__(self)

        self.set_label(label)
        self.set_label_align(0.0, 0.0)

        self.box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box.set_margin_bottom(5)
        self.box.set_margin_left(2)
        self.text_entry = Gtk.Entry()
        self.confirm_button = Gtk.Button(label="Set")

        self.get_style_context().add_class("value-entry")

        self.box.pack_start(self.text_entry, False, False, 0)
        self.box.pack_start(self.confirm_button, False, False, 5)
        self.add(self.box)
        self.show_all()

        self.confirm_button.connect("clicked", lambda btn: self._handle_confirm_click())

        self.on_value_entered = EventBroadcaster()

    def set_value(self, value):
        """
        @type value: str
        """
        self.text_entry.set_text(value)

    def _handle_confirm_click(self):
        value = self.text_entry.get_text()
        self.set_value("")

        self.on_value_entered.notify(value)
        self.hide()

    def toggle(self):
        if self.props.visible:
            self.hide()
        else:
            self.show()


class Drawable(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.position = Vector(0, 0)
        self.margin = Margin()
        self.children = []
        self._visible = True

        self.click_handler = ClickHandler(self)

        self.on_mouse_click = EventBroadcaster()
        self.on_mouse_enter = EventBroadcaster()
        self.on_mouse_leave = EventBroadcaster()

        self.on_mouse_click.subscribe(self.handle_mouse_click)
        self.on_mouse_enter.subscribe(self.handle_mouse_enter)
        self.on_mouse_leave.subscribe(self.handle_mouse_leave)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    def add_child(self, child):
        self.children.append(child)
        self.click_handler.propagate_handler(child.click_handler)

    def set_position(self, position):
        self.position = position.copy()
        self.place_children()

    def handle_mouse_event(self, mouse_data):
        """
        @type mouse_data: drawing.mouse.MouseData
        """
        self.click_handler.handle_mouse_event(mouse_data)

    def handle_mouse_click(self, mouse_data):
        """
        @type mouse_data: drawing.mouse.MouseData
        """
        pass

    def handle_mouse_enter(self, mouse_data):
        """
        @type mouse_data: drawing.mouse.MouseData
        """
        pass

    def handle_mouse_leave(self, mouse_data):
        """
        @type mouse_data: drawing.mouse.MouseData
        """
        pass

    def get_rect(self):
        if not self.visible:
            return RectangleBBox(self.position)

        self.place_children()

        size = RectangleBBox(self.position)

        return RectangleBBox.contain([size] + [child.get_rect() + child.margin for child in self.children if child.visible])

    def place_children(self):
        pass

    def draw(self):
        self.place_children()

        if self.visible:
            for child in self.children:
                child.draw()


class LinearLayoutDirection(Enum):
    Horizontal = 1
    Vertical = 2


class LinearLayout(Drawable):
    def __init__(self, canvas, direction=LinearLayoutDirection.Vertical):
        """
        @type canvas: canvas.Canvas
        @type direction: LinearLayoutDirection
        """
        super(LinearLayout, self).__init__(canvas)
        self.direction = direction

    def place_children(self):
        position = self.position.copy()

        for child in self.children:
            child_position = position + Vector(child.margin.left, child.margin.top)  # add margin
            child.set_position(child_position)
            rect = child.get_rect()

            if self.direction == LinearLayoutDirection.Horizontal:
                position.x += child.margin.left + rect.width + child.margin.right
            elif self.direction == LinearLayoutDirection.Vertical:
                position.y += child.margin.top + rect.height + child.margin.bottom


class ToggleDrawable(Drawable):
    def __init__(self, canvas, drawables):
        """
        Represents a drawable that toggles several drawables on a mouse click.
        @type canvas: canvas.Canvas
        @type drawables: list of Drawable
        """
        super(ToggleDrawable, self).__init__(canvas)

        self.drawables = list(drawables)
        self.current_drawable = 0

    def set_position(self, position):
        """
        @type position: drawing.vector.Vector
        """
        super(ToggleDrawable, self).set_position(position)
        for drawable in self.drawables:
            drawable.set_position(position)

    def get_active_drawable(self):
        return self.drawables[self.current_drawable]

    def get_rect(self):
        return self.get_active_drawable().get_rect()

    def handle_mouse_click(self, mouse_data):
        """
        @type mouse_data: drawing.mouse.MouseData
        """
        self.current_drawable = (self.current_drawable + 1) % len(self.drawables)

    def draw(self):
        self.get_active_drawable().draw()


class Label(Drawable):
    def __init__(self, canvas, label, padding=None, font_style=None, border_width=1):
        """
        @type canvas: canvas.Canvas
        @type label: str | callable
        @type padding: Margin
        @type font_style: FontStyle
        @type border_width: int
        """
        super(Label, self).__init__(canvas)

        if not font_style:
            font_style = FontStyle()

        self.font_style = font_style
        self.label = label if label is not None else ""
        self.padding = padding if padding else Margin.all(5)
        self.border_width = border_width

    def get_label(self):
        if isinstance(self.label, basestring):
            return self.label
        else:
            return self.label()

    def get_rect(self):
        if not self.visible:
            return RectangleBBox(self.position)

        label_size = DrawingUtils.get_text_size(self.canvas, self.get_label(), font_style=self.font_style)

        width = self.border_width + self.padding.left + label_size.width + self.padding.right + self.border_width
        height = self.border_width + self.padding.top + label_size.height + self.padding.bottom + self.border_width

        return RectangleBBox(self.position, Size(width, height))

    def draw(self):
        if not self.visible:
            return

        rect = self.get_rect()

        # box
        DrawingUtils.draw_rectangle(self.canvas, self.position, rect.size, width=self.border_width, center=False)

        text_x = self.position.x + self.padding.left
        text_y = self.position.y + self.padding.top

        # value
        DrawingUtils.draw_text(self.canvas, self.get_label(), Vector(text_x, text_y), y_center=False, font_style=self.font_style)


class LabelWrapper(LinearLayout):
    def __init__(self, canvas, name, inner_drawable, padding=None):
        """
        @type canvas: canvas.Canvas
        @type name: basestring
        @type inner_drawable: Drawable
        """
        super(LabelWrapper, self).__init__(canvas, LinearLayoutDirection.Horizontal)

        self.name = name

        name_child = Label(canvas, name, padding if padding else Margin.all(5))
        self.add_child(name_child)
        self.add_child(inner_drawable)

    def set_show_name(self, value):
        if value:
            self.children[0].visible = True
        else:
            self.children[0].visible = False

        self.place_children()


class Image(Drawable):
    def __init__(self, canvas, image_path, size=None):
        """
        Represents a drawable image.
        Image path has to be a valid path to a PNG image.
        @type canvas: canvas.Canvas
        @type image_path: basestring
        @type size: Size
        """
        super(Image, self).__init__(canvas)

        self.img = cairo.ImageSurface.create_from_png(image_path)
        self.size = size if size else Size(self.img.get_width(), self.img.get_height())

    def get_rect(self):
        return RectangleBBox(self.position, self.size)

    def get_image(self):
        return self.img

    def draw(self):
        DrawingUtils.draw_image_from_surface(self.canvas, self.position, self.get_image(), self.size)


class VariableDrawable(Label):
    def __init__(self, canvas, variable):
        """
        @type canvas: canvas.Canvas
        @type variable: variable.Variable
        """
        super(VariableDrawable, self).__init__(canvas, self.get_variable_value, Margin.all(5))

        self.variable = variable

        self.value_entry = ValueEntry("Edit value of {}".format(variable.name))
        self.value_entry.on_value_entered.subscribe(self._handle_value_change)
        canvas.fixed_wrapper.put(self.value_entry, self.position.x, self.position.y)
        self.value_entry.hide()

    def get_variable_value(self):
        return self.variable.value

    def _handle_value_change(self, value):
        self.variable.value = value

    def handle_mouse_click(self, mouse_data):
        """
        @type mouse_data: mouse.MouseData
        """
        self.value_entry.set_value(self.get_variable_value())
        self.value_entry.toggle()
        self.canvas.fixed_wrapper.move(self.value_entry, mouse_data.position.x, mouse_data.position.y)


class StackFrameDrawable(LinearLayout):
    def __init__(self, canvas, frame):
        """
        @type canvas: canvas.Canvas
        @type frame: frame.Frame
        """
        super(StackFrameDrawable, self).__init__(canvas, LinearLayoutDirection.Vertical)

        self.label = Label(canvas, "Frame {0}".format(frame.func), Margin.all(5), FontStyle(italic=True), 0)
        self.add_child(self.label)

        for var in frame.variables:
            drawable = canvas.memtoview.transform_var(var)
            if drawable:
                drawable = LabelWrapper(self.canvas, "{} {}".format(var.type.name, var.name), drawable)
                self.add_child(drawable)

    def get_rect(self):
        rect = super(StackFrameDrawable, self).get_rect()
        size = rect.size.copy()
        size = Size(size.width + 1, size.height + 1)
        return RectangleBBox(rect.position.copy().add((-1, -1)), size)

    def draw(self):
        super(StackFrameDrawable, self).draw()
        DrawingUtils.draw_rectangle(self.canvas, self.position, self.get_rect().size)


class PointerDrawable(Drawable):
    def __init__(self, canvas, pointer):
        """
        @type canvas: canvas.Canvas
        @type pointer: variable.Variable
        """
        super(PointerDrawable, self).__init__(canvas)
        self.pointer = pointer


class VectorValueDrawable(Label):
    def __init__(self, canvas, variable):
        """
        @type canvas: canvas.Canvas
        @type variable: variable.Variable
        """
        super(VectorValueDrawable, self).__init__(canvas, self.get_name)
        self.variable = variable

    def get_name(self):
        if self.variable.type.type_category in (TypeCategory.Builtin, TypeCategory.String):
            return str(self.variable.value)
        else:
            return "C"


class VectorDrawable(LinearLayout):
    def __init__(self, canvas, vector):
        """
        @type canvas: drawing.canvas.Canvas
        @type vector: variable.Variable
        """
        super(VectorDrawable, self).__init__(canvas, LinearLayoutDirection.Horizontal)
        self.vector = vector
        self.max_elements = 3

        for i in xrange(0, min((self.max_elements, len(vector.children)))):
            self.add_child(VectorValueDrawable(self.canvas, vector.children[i]))

        if len(vector.children) > self.max_elements:
            self.add_child(Label(self.canvas, "..."))

    def get_max_elements(self):
        """
        @rtype: int
        """
        return self.max_elements


class StructDrawable(LinearLayout):
    def __init__(self, canvas, struct):
        """
        @type canvas: canvas.Canvas
        @type struct: variable.Variable
        """
        super(StructDrawable, self).__init__(canvas, LinearLayoutDirection.Vertical)
        self.struct = struct

        for child in struct.children:
            drawable = self.canvas.memtoview.transform_var(child)
            if drawable:
                wrapper = LabelWrapper(self.canvas, child.name, drawable, Margin.all(5))
                self.add_child(wrapper)

    def get_rect(self):
        rect = super(StructDrawable, self).get_rect()
        size = rect.size.copy()
        size = Size(size.width + 1, size.height + 1)
        return RectangleBBox(rect.position.copy().add((-1, -1)), size)

    def draw(self):
        super(StructDrawable, self).draw()
        DrawingUtils.draw_rectangle(self.canvas, self.position, self.get_rect().size)
