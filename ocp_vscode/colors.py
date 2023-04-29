from colorsys import hsv_to_rgb, rgb_to_hsv
from random import randrange, seed, random
from webcolors import name_to_rgb

try:
    import matplotlib as mpl
    import numpy as np

    HAS_MATPLOTLIB = True

except:
    HAS_MATPLOTLIB = False


COLORMAP = None


def get_colormap():
    if COLORMAP is not None:
        COLORMAP.reset()
    return COLORMAP


def set_colormap(colormap):
    global COLORMAP
    COLORMAP = colormap


def unset_colormap():
    global COLORMAP
    COLORMAP = None


#
# Source: matplotlib. This is the minimum set of colormaps without installing matplotlib
#

colormaps = {
    "Accent": (
        (0.4980392156862745, 0.788235294117647, 0.4980392156862745),
        (0.7450980392156863, 0.6823529411764706, 0.8313725490196079),
        (0.9921568627450981, 0.7529411764705882, 0.5254901960784314),
        (1.0, 1.0, 0.6),
        (0.2196078431372549, 0.4235294117647059, 0.6901960784313725),
        (0.9411764705882353, 0.00784313725490196, 0.4980392156862745),
        (0.7490196078431373, 0.3568627450980392, 0.09019607843137253),
        (0.4, 0.4, 0.4),
    ),
    "Dark2": (
        (0.10588235294117647, 0.6196078431372549, 0.4666666666666667),
        (0.8509803921568627, 0.37254901960784315, 0.00784313725490196),
        (0.4588235294117647, 0.4392156862745098, 0.7019607843137254),
        (0.9058823529411765, 0.1607843137254902, 0.5411764705882353),
        (0.4, 0.6509803921568628, 0.11764705882352941),
        (0.9019607843137255, 0.6705882352941176, 0.00784313725490196),
        (0.6509803921568628, 0.4627450980392157, 0.11372549019607843),
        (0.4, 0.4, 0.4),
    ),
    "Paired": (
        (0.6509803921568628, 0.807843137254902, 0.8901960784313725),
        (0.12156862745098039, 0.47058823529411764, 0.7058823529411765),
        (0.6980392156862745, 0.8745098039215686, 0.5411764705882353),
        (0.2, 0.6274509803921569, 0.17254901960784313),
        (0.984313725490196, 0.6039215686274509, 0.6),
        (0.8901960784313725, 0.10196078431372549, 0.10980392156862745),
        (0.9921568627450981, 0.7490196078431373, 0.43529411764705883),
        (1.0, 0.4980392156862745, 0.0),
        (0.792156862745098, 0.6980392156862745, 0.8392156862745098),
        (0.41568627450980394, 0.23921568627450981, 0.6039215686274509),
        (1.0, 1.0, 0.6),
        (0.6941176470588235, 0.34901960784313724, 0.1568627450980392),
    ),
    "Pastel1": (
        (0.984313725490196, 0.7058823529411765, 0.6823529411764706),
        (0.7019607843137254, 0.803921568627451, 0.8901960784313725),
        (0.8, 0.9215686274509803, 0.7725490196078432),
        (0.8705882352941177, 0.796078431372549, 0.8941176470588236),
        (0.996078431372549, 0.8509803921568627, 0.6509803921568628),
        (1.0, 1.0, 0.8),
        (0.8980392156862745, 0.8470588235294118, 0.7411764705882353),
        (0.9921568627450981, 0.8549019607843137, 0.9254901960784314),
        (0.9490196078431372, 0.9490196078431372, 0.9490196078431372),
    ),
    "Pastel2": (
        (0.7019607843137254, 0.8862745098039215, 0.803921568627451),
        (0.9921568627450981, 0.803921568627451, 0.6745098039215687),
        (0.796078431372549, 0.8352941176470589, 0.9098039215686274),
        (0.9568627450980393, 0.792156862745098, 0.8941176470588236),
        (0.9019607843137255, 0.9607843137254902, 0.788235294117647),
        (1.0, 0.9490196078431372, 0.6823529411764706),
        (0.9450980392156862, 0.8862745098039215, 0.8),
        (0.8, 0.8, 0.8),
    ),
    "Set1": (
        (0.8941176470588236, 0.10196078431372549, 0.10980392156862745),
        (0.21568627450980393, 0.49411764705882355, 0.7215686274509804),
        (0.30196078431372547, 0.6862745098039216, 0.2901960784313726),
        (0.596078431372549, 0.3058823529411765, 0.6392156862745098),
        (1.0, 0.4980392156862745, 0.0),
        (1.0, 1.0, 0.2),
        (0.6509803921568628, 0.33725490196078434, 0.1568627450980392),
        (0.9686274509803922, 0.5058823529411764, 0.7490196078431373),
        (0.6, 0.6, 0.6),
    ),
    "Set2": (
        (0.4, 0.7607843137254902, 0.6470588235294118),
        (0.9882352941176471, 0.5529411764705883, 0.3843137254901961),
        (0.5529411764705883, 0.6274509803921569, 0.796078431372549),
        (0.9058823529411765, 0.5411764705882353, 0.7647058823529411),
        (0.6509803921568628, 0.8470588235294118, 0.32941176470588235),
        (1.0, 0.8509803921568627, 0.1843137254901961),
        (0.8980392156862745, 0.7686274509803922, 0.5803921568627451),
        (0.7019607843137254, 0.7019607843137254, 0.7019607843137254),
    ),
    "Set3": (
        (0.5529411764705883, 0.8274509803921568, 0.7803921568627451),
        (1.0, 1.0, 0.7019607843137254),
        (0.7450980392156863, 0.7294117647058823, 0.8549019607843137),
        (0.984313725490196, 0.5019607843137255, 0.4470588235294118),
        (0.5019607843137255, 0.6941176470588235, 0.8274509803921568),
        (0.9921568627450981, 0.7058823529411765, 0.3843137254901961),
        (0.7019607843137254, 0.8705882352941177, 0.4117647058823529),
        (0.9882352941176471, 0.803921568627451, 0.8980392156862745),
        (0.8509803921568627, 0.8509803921568627, 0.8509803921568627),
        (0.7372549019607844, 0.5019607843137255, 0.7411764705882353),
        (0.8, 0.9215686274509803, 0.7725490196078432),
        (1.0, 0.9294117647058824, 0.43529411764705883),
    ),
    "tab10": (
        (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
        (1.0, 0.4980392156862745, 0.054901960784313725),
        (0.17254901960784313, 0.6274509803921569, 0.17254901960784313),
        (0.8392156862745098, 0.15294117647058825, 0.1568627450980392),
        (0.5803921568627451, 0.403921568627451, 0.7411764705882353),
        (0.5490196078431373, 0.33725490196078434, 0.29411764705882354),
        (0.8901960784313725, 0.4666666666666667, 0.7607843137254902),
        (0.4980392156862745, 0.4980392156862745, 0.4980392156862745),
        (0.7372549019607844, 0.7411764705882353, 0.13333333333333333),
        (0.09019607843137255, 0.7450980392156863, 0.8117647058823529),
    ),
    "tab20": (
        (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
        (0.6823529411764706, 0.7803921568627451, 0.9098039215686274),
        (1.0, 0.4980392156862745, 0.054901960784313725),
        (1.0, 0.7333333333333333, 0.47058823529411764),
        (0.17254901960784313, 0.6274509803921569, 0.17254901960784313),
        (0.596078431372549, 0.8745098039215686, 0.5411764705882353),
        (0.8392156862745098, 0.15294117647058825, 0.1568627450980392),
        (1.0, 0.596078431372549, 0.5882352941176471),
        (0.5803921568627451, 0.403921568627451, 0.7411764705882353),
        (0.7725490196078432, 0.6901960784313725, 0.8352941176470589),
        (0.5490196078431373, 0.33725490196078434, 0.29411764705882354),
        (0.7686274509803922, 0.611764705882353, 0.5803921568627451),
        (0.8901960784313725, 0.4666666666666667, 0.7607843137254902),
        (0.9686274509803922, 0.7137254901960784, 0.8235294117647058),
        (0.4980392156862745, 0.4980392156862745, 0.4980392156862745),
        (0.7803921568627451, 0.7803921568627451, 0.7803921568627451),
        (0.7372549019607844, 0.7411764705882353, 0.13333333333333333),
        (0.8588235294117647, 0.8588235294117647, 0.5529411764705883),
        (0.09019607843137255, 0.7450980392156863, 0.8117647058823529),
        (0.6196078431372549, 0.8549019607843137, 0.8980392156862745),
    ),
    "tab20b": (
        (0.2235294117647059, 0.23137254901960785, 0.4745098039215686),
        (0.3215686274509804, 0.32941176470588235, 0.6392156862745098),
        (0.4196078431372549, 0.43137254901960786, 0.8117647058823529),
        (0.611764705882353, 0.6196078431372549, 0.8705882352941177),
        (0.38823529411764707, 0.4745098039215686, 0.2235294117647059),
        (0.5490196078431373, 0.6352941176470588, 0.3215686274509804),
        (0.7098039215686275, 0.8117647058823529, 0.4196078431372549),
        (0.807843137254902, 0.8588235294117647, 0.611764705882353),
        (0.5490196078431373, 0.42745098039215684, 0.19215686274509805),
        (0.7411764705882353, 0.6196078431372549, 0.2235294117647059),
        (0.9058823529411765, 0.7294117647058823, 0.3215686274509804),
        (0.9058823529411765, 0.796078431372549, 0.5803921568627451),
        (0.5176470588235295, 0.23529411764705882, 0.2235294117647059),
        (0.6784313725490196, 0.28627450980392155, 0.2901960784313726),
        (0.8392156862745098, 0.3803921568627451, 0.4196078431372549),
        (0.9058823529411765, 0.5882352941176471, 0.611764705882353),
        (0.4823529411764706, 0.2549019607843137, 0.45098039215686275),
        (0.6470588235294118, 0.3176470588235294, 0.5803921568627451),
        (0.807843137254902, 0.42745098039215684, 0.7411764705882353),
        (0.8705882352941177, 0.6196078431372549, 0.8392156862745098),
    ),
    "tab20c": (
        (0.19215686274509805, 0.5098039215686274, 0.7411764705882353),
        (0.4196078431372549, 0.6823529411764706, 0.8392156862745098),
        (0.6196078431372549, 0.792156862745098, 0.8823529411764706),
        (0.7764705882352941, 0.8588235294117647, 0.9372549019607843),
        (0.9019607843137255, 0.3333333333333333, 0.050980392156862744),
        (0.9921568627450981, 0.5529411764705883, 0.23529411764705882),
        (0.9921568627450981, 0.6823529411764706, 0.4196078431372549),
        (0.9921568627450981, 0.8156862745098039, 0.6352941176470588),
        (0.19215686274509805, 0.6392156862745098, 0.32941176470588235),
        (0.4549019607843137, 0.7686274509803922, 0.4627450980392157),
        (0.6313725490196078, 0.8509803921568627, 0.6078431372549019),
        (0.7803921568627451, 0.9137254901960784, 0.7529411764705882),
        (0.4588235294117647, 0.4196078431372549, 0.6941176470588235),
        (0.6196078431372549, 0.6039215686274509, 0.7843137254901961),
        (0.7372549019607844, 0.7411764705882353, 0.8627450980392157),
        (0.8549019607843137, 0.8549019607843137, 0.9215686274509803),
        (0.38823529411764707, 0.38823529411764707, 0.38823529411764707),
        (0.5882352941176471, 0.5882352941176471, 0.5882352941176471),
        (0.7411764705882353, 0.7411764705882353, 0.7411764705882353),
        (0.8509803921568627, 0.8509803921568627, 0.8509803921568627),
    ),
}


def hsv_mapper(t, saturation=0.6, value=0.95):
    return hsv_to_rgb(t, saturation, value)


def matplotlib_mapper(t, name):
    if not HAS_MATPLOTLIB:
        raise RuntimeError("matplotlib is not installed")

    colormap = mpl.colormaps.get(name)

    if name is None:
        raise ValueError(f"No colormap named '{name}' in matplotlib")
    if not isinstance(colormap, mpl.colors.LinearSegmentedColormap):
        raise ValueError(
            f"The colormap named '{name}' is not a linear segemented colormap"
        )

    color = colormap(t)[:3]
    return (color[0].item(), color[1].item(), color[2].item())


def random_rgb_mapper(lower=0, upper=255, brightness=1):
    r = randrange(lower, upper) / 255
    g = randrange(lower, upper) / 255
    b = randrange(lower, upper) / 255
    h, s, v = rgb_to_hsv(r, g, b)
    r, g, b = hsv_to_rgb(h, s, min(1, brightness * v))
    return (r, g, b)


def web_to_rgb(name):
    rgb = name_to_rgb(name)
    return (rgb.red / 255, rgb.green / 255, rgb.blue / 255)


class ColorMap:
    def __init__(self):
        self.index = 0
        self.alpha = 1.0

    def __iter__(self):
        return self

    def reset(self):
        self.index = 0


class ListedColorMap(ColorMap):
    def __init__(self, colors, alpha=1.0, reverse=False):
        super().__init__()

        self.colors = []
        for i in range(len(colors)):
            if isinstance(colors[i], str):
                self.colors.append(web_to_rgb(colors[i]))
            else:
                self.colors.append(colors[i])
        if reverse:
            self.colors = list(reversed(self.colors))

        self.alpha = alpha
        self.n = len(self.colors)

    def __next__(self):
        if self.index >= self.n:
            self.index = 0
        elem = self.colors[self.index]
        self.index += 1
        return (*elem, self.alpha)


class SegmentedColorMap(ColorMap):
    def __init__(self, length, mapper, alpha=1.0, reverse=False, **params):
        super().__init__()

        self.mapper = mapper
        self.length = length
        self.params = params
        self.alpha = alpha
        self.reverse = reverse

    def __next__(self):
        if self.index >= self.length:
            self.index = 0
        t = self.index / self.length
        if self.reverse:
            t = 1 - t
        color = self.mapper(t, **self.params)
        self.index += 1
        return (*color, self.alpha)


class GoldenRatioColormap(ColorMap):
    def __init__(self, mapper, alpha=1.0, reverse=False, **params):
        super().__init__()

        self.mapper = mapper
        self.params = params
        self.alpha = alpha
        self.reverse = reverse

    def __next__(self):
        phi_inv = 2 / (1 + 5**0.5)
        t = (phi_inv * self.index) % 1
        if self.reverse:
            t = 1 - t
        color = self.mapper(t, **self.params)

        self.index += 1
        return (*color, self.alpha)


class SeededColormap(ColorMap):
    def __init__(self, seed_value, mapper, alpha=1.0, no_param=False, **params):
        super().__init__()

        self.mapper = mapper
        self.params = params
        self.seed_value = seed_value
        self.alpha = alpha
        self.no_param = no_param

        self.reset()

    def __next__(self):
        if self.no_param:
            color = self.mapper(**self.params)
        else:
            t = random()
            color = self.mapper(t, **self.params)
        return (*color, self.alpha)

    def reset(self):
        seed(self.seed_value)


class CM:
    @staticmethod
    def accent(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["Accent"], alpha=alpha, reverse=reverse)

    @staticmethod
    def dark2(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["Dark2"], alpha=alpha, reverse=reverse)

    @staticmethod
    def paired(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["Paired"], alpha=alpha, reverse=reverse)

    @staticmethod
    def pastel1(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["Pastel1"], alpha=alpha, reverse=reverse)

    @staticmethod
    def pastel2(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["Pastel2"], alpha=alpha, reverse=reverse)

    @staticmethod
    def set1(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["Set1"], alpha=alpha, reverse=reverse)

    @staticmethod
    def set2(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["Set2"], alpha=alpha, reverse=reverse)

    @staticmethod
    def set3(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["Set3"], alpha=alpha, reverse=reverse)

    @staticmethod
    def tab10(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["tab10"], alpha=alpha, reverse=reverse)

    @staticmethod
    def tab20(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["tab20"], alpha=alpha, reverse=reverse)

    @staticmethod
    def tab20b(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["tab20b"], alpha=alpha, reverse=reverse)

    @staticmethod
    def tab20c(alpha=1.0, reverse=False):
        return ListedColorMap(colormaps["tab20c"], alpha=alpha, reverse=reverse)

    @staticmethod
    def golden_ratio(colormap="hsv", alpha=1.0, reverse=False):
        if colormap == "hsv":
            return GoldenRatioColormap(hsv_mapper, alpha=alpha, reverse=reverse)
        elif colormap.startswith("mpl"):
            _, name = colormap.split(":")
            return GoldenRatioColormap(
                matplotlib_mapper, alpha=alpha, reverse=reverse, name=name
            )

    @staticmethod
    def seeded(seed_value=42, colormap="hsv", alpha=1.0, **params):
        if colormap == "hsv":
            return SeededColormap(seed_value, hsv_mapper, alpha=alpha)
        elif colormap == "rgb":
            return SeededColormap(
                seed_value, random_rgb_mapper, alpha=alpha, no_param=True, **params
            )
        elif colormap.startswith("mpl"):
            _, name = colormap.split(":")
            return SeededColormap(seed_value, matplotlib_mapper, alpha=alpha, name=name)

    @staticmethod
    def segmented(length=10, colormap="hsv", alpha=1.0, reverse=False):
        if colormap == "hsv":
            return SegmentedColorMap(length, hsv_mapper, alpha=alpha, reverse=reverse)
        elif colormap.startswith("mpl"):
            _, name = colormap.split(":")
            return SegmentedColorMap(
                length, matplotlib_mapper, alpha=alpha, name=name, reverse=reverse
            )
