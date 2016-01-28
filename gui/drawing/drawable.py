# -*- coding: utf-8 -*-

import abc
import cairo

from gi.repository import Gtk

from enum import Enum

from drawing.geometry import Margin, RectangleBBox, Padding
from drawing.size import Size
from drawing.vector import Vector
from enums import TypeCategory
from gui_util import require_gui_thread
from util import EventBroadcaster
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
    @staticmethod
    def make_color(color):
        """
        @type color: Color | tuple of float
        @rtype: Color
        """
        if isinstance(color, Color):
            return color.copy()
        else:
            return Color(color[0], color[1], color[2], color[3])

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

    def copy(self):
        return Color(self.red, self.green, self.blue, self.alpha)


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
    def draw_rectangle(canvas, position, size, color=Color(), width=1, center=False, stroke=True):
        cr = canvas.cr
        cr.save()

        position = Vector.vectorize(position)
        size = Size.make_size(size)

        if center:
            position.x -= size.width / 2
            position.y -= size.height / 2

        DrawingUtils.set_color(canvas, color)
        cr.rectangle(position.x, position.y, size.width, size.height)

        if stroke:
            cr.set_line_width(width)
            cr.stroke()
        else:
            cr.fill()

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


class Drawable(object):
    @staticmethod
    def get_default_bg_color():
        return Color(0.5, 0.5, 0.5, 1.0)

    @require_gui_thread
    def __init__(self, canvas, **properties):
        self.canvas = canvas

        self.position = self._parse_property(properties, "position", Vector(0, 0), Vector.vectorize)
        """@type position: drawing.vector.Vector"""
        self.margin = self._parse_property(properties, "margin", Margin.all(0))
        """@type margin: drawing.geometry.Margin"""
        self.padding = self._parse_property(properties, "padding", Padding.all(0))
        """@type padding: drawing.geometry.Padding"""
        self.request_size = self._parse_property(properties, "size", Size(-1, -1), Size.make_size)
        """@type request_size: drawing.size.Size"""
        self.min_size = self._parse_property(properties, "min_size", Size(0, 0), Size.make_size)
        """@type min_size: drawing.size.Size"""
        self.max_size = self._parse_property(properties, "max_size", Size(999, 999), Size.make_size)
        """@type max_size: drawing.size.Size"""
        self.bg_color = self._parse_property(properties, "bg_color", Drawable.get_default_bg_color(), Color.make_color)
        """@type bg_color: drawing.drawable.Color"""

        self.children = []
        self._visible = True

        self.click_handler = ClickHandler(self)

        self.on_mouse_click = EventBroadcaster()
        self.on_mouse_enter = EventBroadcaster()
        self.on_mouse_leave = EventBroadcaster()

        self.on_mouse_click.subscribe(self.handle_mouse_click)
        self.on_mouse_enter.subscribe(self.handle_mouse_enter)
        self.on_mouse_enter.subscribe(self.handle_tooltip_start)
        self.on_mouse_leave.subscribe(self.handle_mouse_leave)
        self.on_mouse_leave.subscribe(self.handle_tooltip_end)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    def get_content_size(self):
        raise NotImplementedError()

    def get_computed_size(self):
        content_size = self.get_content_size()

        width = self.request_size.width if self.request_size.width >= 0 else content_size.width
        height = self.request_size.height if self.request_size.height >= 0 else content_size.height

        width = max((width, self.min_size.width))
        height = max((height, self.min_size.height))

        width = min((width, self.max_size.width))
        height = min((height, self.max_size.height))

        return Size(width, height)

    def add_child(self, child):
        self.children.append(child)
        self.click_handler.propagate_handler(child.click_handler)
        self.place_children()  # TODO: place children after their visibility changes

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

    def handle_tooltip_start(self, mouse_data):
        """
        @type mouse_data: mouse.MouseData
        """
        tooltip = self.get_tooltip()

        if tooltip is not None:
            self.canvas.set_drawable_tooltip(self, tooltip)

    def handle_tooltip_end(self, mouse_data):
        """
        @type mouse_data: mouse.MouseData
        """
        self.canvas.set_drawable_tooltip(self, None)

    def get_tooltip(self):
        """
        @rtype: basestring | None
        """
        return None

    def get_rect(self):
        if not self.visible:
            return RectangleBBox(self.position)

        return RectangleBBox(self.position, self.get_computed_size() + self.padding.to_size())

    def place_children(self):
        pass

    def draw(self):
        if self.visible:
            for child in self.children:
                child.draw()

    def _parse_property(self, properties, key, default, modifier=None):
        """
        Parses property from property dictionary.
        Modifier modifies the resulting value.
        @type properties: dict
        @type key: basestring
        @type default: object
        @type modifier: function
        @rtype: object
        """
        if key in properties:
            if modifier:
                return modifier(properties[key])
            else:
                return properties[key]
        else:
            return default


class LinearLayoutDirection(Enum):
    Horizontal = 1
    Vertical = 2


class LinearLayout(Drawable):
    def __init__(self, canvas, direction=LinearLayoutDirection.Vertical, **properties):
        """
        @type canvas: canvas.Canvas
        @type direction: LinearLayoutDirection
        """
        super(LinearLayout, self).__init__(canvas, **properties)
        self.direction = direction

    def place_children(self):
        position = self.position.copy()
        position.x += self.padding.left
        position.y += self.padding.top

        for child in self.children:
            child_position = position + Vector(child.margin.left, child.margin.top)  # add margin
            child.set_position(child_position)
            rect = child.get_rect()

            if self.direction == LinearLayoutDirection.Horizontal:
                position.x += child.margin.left + rect.width + child.margin.right
            elif self.direction == LinearLayoutDirection.Vertical:
                position.y += child.margin.top + rect.height + child.margin.bottom

    def get_content_size(self):
        rectangle = RectangleBBox.contain([child.get_rect() + child.margin for child in self.children if child.visible])
        return (rectangle + self.padding).size


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
    def __init__(self, canvas, label, font_style=None, **properties):
        """
        @type canvas: canvas.Canvas
        @type label: str | callable
        @type padding: Margin
        @type font_style: FontStyle
        """
        super(Label, self).__init__(canvas, **properties)

        if not font_style:
            font_style = FontStyle()

        self.font_style = font_style
        self.label = label if label is not None else ""

    def get_label(self):
        if isinstance(self.label, basestring):
            return self.label
        else:
            return self.label()

    def get_ellipsized_label(self):
        label = self.get_label()
        width = self.get_computed_size().width
        text_width = self.get_content_size()

        if text_width.width <= width:
            return label

        next_skip = False

        for i in xrange(len(label)):
            if next_skip:
                next_skip = False
                continue

            char = ord(label[i])
            if (char & 0b11100000) == 0b11000000:   # skip two byte UTF-8
                next_skip = True

            label_test = label[:i] + "..."
            if DrawingUtils.get_text_size(self.canvas, label_test, self.font_style).width > width:
                if i == 0:
                    return ""
                else:
                    return label[:(i - 1)] + "..."

        return label

    def get_content_size(self):
        return DrawingUtils.get_text_size(self.canvas, self.get_label(), font_style=self.font_style)

    def get_rect(self):
        if not self.visible:
            return RectangleBBox(self.position)

        return Drawable.get_rect(self)

    def get_tooltip(self):
        return self.get_label()

    def draw(self):
        if not self.visible:
            return

        rect = self.get_rect()

        # box
        DrawingUtils.draw_rectangle(self.canvas, self.position, rect.size,
                                    center=False, color=self.bg_color, stroke=False)

        text_x = self.position.x + rect.width / 2.0  # self.position.x + self.padding.left
        text_y = self.position.y + rect.height / 2.0  # self.position.y + self.padding.top

        # value
        DrawingUtils.draw_text(self.canvas, self.get_ellipsized_label(), Vector(text_x, text_y), y_center=True, x_center=True, font_style=self.font_style)


class LabelWrapper(LinearLayout):
    def __init__(self, canvas, label, inner_drawable):
        """
        @type canvas: canvas.Canvas
        @type label: Label
        @type inner_drawable: Drawable
        """
        super(LabelWrapper, self).__init__(canvas, LinearLayoutDirection.Horizontal)
        self.label = label
        self.inner_drawable = inner_drawable

        self.add_child(self.label)
        self.add_child(self.inner_drawable)

    def set_show_name(self, value):
        if value:
            self.children[0].visible = True
        else:
            self.children[0].visible = False

        self.place_children()


class Image(Drawable):
    def __init__(self, canvas, image_path, **properties):
        """
        Represents a drawable image.
        Image path has to be a valid path to a PNG image.
        @type canvas: canvas.Canvas
        @type image_path: basestring
        @type size: Size
        """
        super(Image, self).__init__(canvas, **properties)

        self.img = cairo.ImageSurface.create_from_png(image_path)

    def get_content_size(self):
        return Size(self.img.get_width(), self.img.get_height())

    def get_image(self):
        return self.img

    def draw(self):
        x = self.position.x + self.padding.left
        y = self.position.y + self.padding.top
        DrawingUtils.draw_image_from_surface(self.canvas, Vector(x, y), self.get_image(), self.get_computed_size())


class VariableDrawable(Label):
    def __init__(self, canvas, variable, **properties):
        """
        @type canvas: canvas.Canvas
        @type variable: debugee.Variable
        """
        self.variable = variable
        super(VariableDrawable, self).__init__(canvas, self.get_variable_value, size=Size(-1, 20), **properties)

    def get_variable_value(self):
        return self.variable.value

    def _handle_value_change(self, value):
        self.variable.value = value

    def handle_mouse_click(self, mouse_data):
        """
        @type mouse_data: mouse.MouseData
        """
        title = "Edit value of {}".format(self.variable.name)
        value = self.get_variable_value()
        self.canvas.fixed_wrapper.toggle_widget_to(self.canvas.fixed_wrapper.text_entry, mouse_data.position.copy(),
                                                   title, value, self._handle_value_change)


class CompositeLabel(LinearLayout):
    def __init__(self, canvas, composite, **properties):
        """
        @type canvas: canvas.Canvas
        @type composite: variable.Variable | debugee.Frame
        """
        super(CompositeLabel, self).__init__(canvas, LinearLayoutDirection.Vertical, **properties)
        self.composite = composite

        label = self.get_composite_label()
        if label:
            self.label = Label(canvas, self.get_composite_label, FontStyle(italic=True), size=Size(-1, 25),
                               padding=Padding.all(5), margin=Margin(0, 0, 5, 0))
            self.add_child(self.label)

        for var in self.get_composite_children():
            drawable = self.create_composite_value(var)
            if drawable:
                self.add_child(drawable)

    def create_composite_value(self, variable):
        """
        @type variable: debugee.Variable
        @rtype: Drawable
        """
        drawable = self.canvas.memtoview.transform_var(variable)
        wrapper = LabelWrapper(self.canvas,
                            Label(self.canvas, "{} {}".format(variable.type.name, variable.name),
                                  min_size=Size(20, 20),
                                  max_size=Size(40, 20),
                                  padding=Padding.all(5),
                                  margin=Margin(0, 1, 0, 0)),
                            drawable)
        wrapper.margin.bottom = 4
        return wrapper

    def get_composite_label(self):
        raise NotImplementedError()

    def get_composite_children(self):
        raise NotImplementedError()


class StackFrameDrawable(CompositeLabel):
    def __init__(self, canvas, frame, **properties):
        """
        @type canvas: canvas.Canvas
        @type frame: debugee.Frame
        """
        super(StackFrameDrawable, self).__init__(canvas, frame, **properties)

        self.label.min_size = Size(100, 25)
        self.label.on_mouse_click.subscribe(self._handle_label_click)

    def _handle_label_click(self, mouse_data):
        """
        @type mouse_data: drawing.mouse.MouseData
        """
        if self.canvas.debugger.thread_manager.get_current_frame().level != self.composite.level:
            self.canvas.debugger.thread_manager.change_frame(self.composite.level)

    def create_composite_value(self, variable):
        drawable = CompositeLabel.create_composite_value(self, variable)
        drawable.label.min_size = Size(60, 20)
        drawable.label.max_size = drawable.label.min_size.copy()
        return drawable

    def get_composite_label(self):
        return "Frame {0}".format(self.composite.func)

    def get_composite_children(self):
        return self.composite.variables

    def draw(self):
        frame = self.canvas.debugger.thread_manager.get_current_frame()

        if frame:
            if frame.level == self.composite.level:
                self.label.bg_color = Color(0.8, 0.2, 0.1)
            else:
                self.label.bg_color = Drawable.get_default_bg_color()

        CompositeLabel.draw(self)


class StructDrawable(CompositeLabel):
    def __init__(self, canvas, struct, **properties):
        """
        @type canvas: canvas.Canvas
        @type struct: debugee.Variable
        """
        super(StructDrawable, self).__init__(canvas, struct, **properties)

    def create_composite_value(self, variable):
        drawable = CompositeLabel.create_composite_value(self, variable)
        drawable.label.min_size = Size(40, 20)
        drawable.label.max_size = drawable.label.min_size.copy()
        drawable.margin.bottom = 1
        return drawable

    def get_composite_label(self):
        return None

    def get_composite_children(self):
        return self.composite.children


class PointerDrawable(Drawable):
    def __init__(self, canvas, pointer):
        """
        @type canvas: canvas.Canvas
        @type pointer: debugee.Variable
        """
        super(PointerDrawable, self).__init__(canvas)
        self.pointer = pointer


class VectorValueDrawable(Label):
    def __init__(self, canvas, variable):
        """
        @type canvas: canvas.Canvas
        @type variable: debugee.Variable
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
        @type vector: debugee.Variable
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
