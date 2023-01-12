from PIL import Image
from PIL.PngImagePlugin import PngInfo

from pond.artifact import Artifact


class PILImageArtifact(Artifact):
    """ Artifact for Matlab figures.
    """

    # --- Artifact class interface

    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        """ Read a Matlab figure artifact from CSV file. """
        image = Image.open(file_)
        metadata = image.info
        return cls(image, metadata)

    @staticmethod
    def filename(basename):
        return basename + '.png'

    # --- PILImageArtifact class interface

    @classmethod
    def from_matplotlib_fig(cls, fig, metadata=None):
        fig.canvas.draw()
        image = Image.frombytes(
            'RGB',
            fig.canvas.get_width_height(),
            fig.canvas.tostring_rgb()
        )
        return cls(image, metadata)

    # --- Artifact interface

    def write_bytes(self, file_, **kwargs):
        png_metadata = PngInfo()
        for key, value in self.metadata.items():
            png_metadata.add_text(key, str(value))

        self.data.save(file_, pnginfo=png_metadata)
