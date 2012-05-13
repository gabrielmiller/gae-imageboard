import os
import webapp2
import jinja2

from google.appengine.ext import db
from google.appengine.api import images

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
	def write(self, *args, **kwargs):
		self.response.out.write(*args, **kwargs)

	def render_str(self, template, **params):
		y = jinja_env.get_template(template)
		return y.render(params)

	def render(self, template, **kwargs):
		self.write(self.render_str(template, **kwargs))

class Postedimage(db.Model):
	title = db.StringProperty(required=True)
	upfile = db.BlobProperty(required=True)
	text = db.TextProperty()
	createdate = db.DateTimeProperty(auto_now_add=True)

class MainPage(Handler):
	def render_page(self, title="", upfile="", text="", error=""):
		postedimages = db.GqlQuery("SELECT * FROM Postedimage ORDER BY createdate DESC")
		self.render("index.html", title=title, upfile=upfile, text=text, error=error, postedimages=postedimages)

	def get(self):
		self.render_page()

	def post(self):
		title = self.request.get("title")
		upfile = self.request.get("upfile")
		text = self.request.get("text")

		if title and upfile:
			z = Postedimage(title=title, upfile=upfile, text=text)
			z.put()
			self.redirect("/")

		else:
			error = "Error: You must specify at least a title and file."
			self.render_page(title, upfile, text, error)

class GetImage (Handler):
     def get(self):
       relayimage = db.get(self.request.get("img_id"))
       if relayimage.upfile:
           self.response.headers['Content-Type'] = "image/jpg"
           self.response.out.write(relayimage.upfile)
       else:
           self.error(404)

app = webapp2.WSGIApplication([('/', MainPage),('/img', GetImage)], debug=True)