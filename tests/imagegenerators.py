
# Copyright 2009 Jaap Karssenberg <jaap.karssenberg@gmail.com>



import tests

from tests.mainwindow import setUpMainWindow

from gi.repository import Gtk

from zim.fs import Dir

from zim.plugins.base.imagegenerator import \
	ImageGeneratorClass, ImageGeneratorDialog, ImageGeneratorPageViewExtensionBase

from zim.plugins.equationeditor import InsertEquationPlugin, EquationGenerator
from zim.plugins.diagrameditor import InsertDiagramPlugin, DiagramGenerator
from zim.plugins.gnu_r_ploteditor import InsertGNURPlotPlugin, GNURPlotGenerator
from zim.plugins.gnuplot_ploteditor import InsertGnuplotPlugin, GnuplotGenerator
from zim.plugins.gnuplot_ploteditor import GnuplotPageViewExtension
from zim.plugins.scoreeditor import InsertScorePlugin, ScoreGenerator
from zim.plugins.ditaaeditor import InsertDitaaPlugin, DitaaGenerator
from zim.plugins.sequencediagrameditor import InsertSequenceDiagramPlugin, SequenceDiagramGenerator


@tests.slowTest
class TestGenerator(tests.TestCase):

	pluginklass = None
	generatorklass = None
	dialogklass = ImageGeneratorDialog

	def _test_generator(self):
		plugin = self.pluginklass()

		attachment_dir = self.setUpFolder(mock=tests.MOCK_ALWAYS_REAL)
		notebook = self.setUpNotebook()
		notebook.get_attachments_dir = lambda *a: attachment_dir
		mainwindow = setUpMainWindow(notebook)

		extensionklass = plugin.extension_classes['PageView']
		self.assertTrue(issubclass(extensionklass, ImageGeneratorPageViewExtensionBase))

		extension = extensionklass(plugin, mainwindow.pageview)

		generator = extension.build_generator()
		self.assertIsInstance(generator, ImageGeneratorClass)

		# Check properties
		self.assertIsNotNone(generator.object_type)
		self.assertIsNotNone(generator.scriptname)
		self.assertIsNotNone(generator.imagename)

		# Input OK
		generator = self.generatorklass(plugin)
		generator.cleanup() # ensure files did not yet exist
		imagefile, logfile = generator.generate_image(self.validinput)
		self.assertTrue(imagefile.exists())
		if generator.uses_log_file:
			self.assertTrue(logfile.exists())
		else:
			self.assertIsNone(logfile)

		# Cleanup
		generator.cleanup()
		self.assertFalse(imagefile.exists())
		if generator.uses_log_file:
			self.assertFalse(logfile.exists())

		# Input NOK
		if self.invalidinput is not None:
			generator = self.generatorklass(plugin)
			imagefile, logfile = generator.generate_image(self.invalidinput)
			self.assertIsNone(imagefile)
			if generator.uses_log_file:
				self.assertTrue(logfile.exists())
			else:
				self.assertIsNone(logfile)

		# Dialog OK
		dialog = self.dialogklass(mainwindow.pageview, '<title>', generator)
		dialog.set_text(self.validinput)
		dialog.assert_response_ok()

		# Dialog NOK
		if self.invalidinput is not None:
			def ok_store(dialog):
				# Click OK in the "Store Anyway" question dialog
				dialog.do_response(Gtk.ResponseType.YES)

			with tests.LoggingFilter('zim.gui.pageview', 'No such image:'):
				with tests.DialogContext(ok_store):
					dialog = self.dialogklass(mainwindow.pageview, '<title>', generator)
					dialog.set_text(self.invalidinput)
					dialog.assert_response_ok()

		# Check menu
		#~ plugin = self.pluginklass(MockUI())
		#~ menu = Gtk.Menu()
		#~ plugin.do_populate_popup(menu, buffer, iter, image)


@tests.skipUnless(InsertEquationPlugin.check_dependencies_ok(), 'Missing dependencies')
class TestEquationEditor(TestGenerator):

	pluginklass = InsertEquationPlugin
	generatorklass = EquationGenerator

	validinput = r'''
c = \sqrt{ a^2 + b^2 }

\int_{-\infty}^{\infty} \frac{1}{x} \, dx

f(x) = \sum_{n = 0}^{\infty} \alpha_n x^n

x_{1,2}=\frac{-b\pm\sqrt{\color{Red}b^2-4ac}}{2a}

\hat a  \bar b  \vec c  x'  \dot{x}  \ddot{x}
'''
	invalidinput = r'\int_{'

	def runTest(self):
		'Test Equation Editor plugin'
		TestGenerator._test_generator(self)


@tests.skipUnless(InsertDiagramPlugin.check_dependencies_ok(), 'Missing dependencies')
class TestDiagramEditor(TestGenerator):

	pluginklass = InsertDiagramPlugin
	generatorklass = DiagramGenerator

	validinput = r'''
digraph G {
	foo -> bar
	bar -> baz
	baz -> foo
}
'''
	invalidinput = r'sdf sdfsdf sdf'

	def runTest(self):
		'Test Diagram Editor plugin'
		TestGenerator._test_generator(self)


@tests.skipUnless(InsertGNURPlotPlugin.check_dependencies_ok(), 'Missing dependencies')
class TestGNURPlotEditor(TestGenerator):

	pluginklass = InsertGNURPlotPlugin
	generatorklass = GNURPlotGenerator

	validinput = r'''
x = seq(-4,4,by=0.01)
y = sin(x) + 1
plot(x,y,type='l')
'''
	invalidinput = r'sdf sdfsdf sdf'

	def runTest(self):
		'Test GNU R Plot Editor plugin'
		TestGenerator._test_generator(self)


@tests.skipUnless(InsertGnuplotPlugin.check_dependencies_ok(), 'Missing dependencies')
class TestGnuplotEditor(TestGenerator):

	pluginklass = InsertGnuplotPlugin
	generatorklass = GnuplotGenerator

	validinput = r'plot sin(x), cos(x)'
	invalidinput = r'sdf sdfsdf sdf'

	def testGenerator(self):
		'Test Gnuplot Plot Editor plugin'
		TestGenerator._test_generator(self)


@tests.skipUnless(InsertScorePlugin.check_dependencies_ok(), 'Missing dependencies')
class TestScoreEditor(TestGenerator):

	pluginklass = InsertScorePlugin
	generatorklass = ScoreGenerator

	validinput = r'''
\version "2.18.2"
\relative c {
        \clef bass
        \key d \major
        \time 4/4

        d4 a b fis
        g4 d g a
}
'''
	invalidinput = r'sdf sdfsdf sdf'

	def runTest(self):
		'Test Score Editor plugin'
		TestGenerator._test_generator(self)



@tests.skipUnless(InsertDitaaPlugin.check_dependencies_ok(), 'Missing dependencies')
class TestDitaaEditor(TestGenerator):

	pluginklass = InsertDitaaPlugin
	generatorklass = DitaaGenerator

	def setUp(self):
		self.validinput = r'''
+--------+   +-------+    +-------+
|        | --+ ditaa +--> |       |
|  Text  |   +-------+    |diagram|
|Document|   |!magic!|    |       |
|     {d}|   |       |    |       |
+---+----+   +-------+    +-------+
    :                         ^
    |       Lots of work      |
    +-------------------------+
'''
		self.invalidinput = None # ditaa seems to render anything ...

	def runTest(self):
		'Test Ditaa Editor plugin'
		TestGenerator._test_generator(self)


@tests.skipUnless(InsertSequenceDiagramPlugin.check_dependencies_ok(), 'Missing dependencies')
class TestSequenceDiagramEditor(TestGenerator):

	pluginklass = InsertSequenceDiagramPlugin
	generatorklass = SequenceDiagramGenerator

	def setUp(self):
		self.validinput = r'''
seqdiag {
  browser  -> webserver [label = "GET /index.html"];
  browser <-- webserver;
  browser  -> webserver [label = "POST /blog/comment"];
              webserver  -> database [label = "INSERT comment"];
              webserver <-- database;
  browser <-- webserver;
}
'''
		self.invalidinput = 'sdfsdf sdfsdf'

	def runTest(self):
		'Test Sequence Diagram Editor plugin'
		TestGenerator._test_generator(self)
