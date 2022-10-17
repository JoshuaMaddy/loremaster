using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using LoreMaster.Models;

namespace LoreMaster.Controllers
{
    public class SheetsController : Controller
    {
        private ApplicationDbContext _dbContext;
        // GET: Sheets

        public SheetsController ()
        {
            _dbContext = new ApplicationDbContext();    
        }
        public ActionResult Index()
        {
            var sheets = _dbContext.Sheets.ToList();
            return View(sheets);
        }

        public ActionResult New()
        {
            return View();
        }

        public ActionResult Add(CharacterSheet sheet)
        {
            //sheet.Owner = System.Web.HttpContext.Current.User.Identity.Name;
            _dbContext.Sheets.Add(sheet);
            _dbContext.SaveChanges();
            return RedirectToAction("Index");
        }

        public ActionResult Edit(int id)
        {
            var sheet = _dbContext.Sheets.SingleOrDefault(v => v.Id == id);
            if (sheet == null)
                return HttpNotFound();
            return View(sheet);
        }

        public ActionResult Delete(int id)
        {
            var sheet = _dbContext.Sheets.SingleOrDefault(v => v.Id == id);
            if (sheet == null)
                return HttpNotFound();
            return View(sheet);
        }

        [HttpPost]
        public ActionResult DoDelete(int id)
        {
            var character = _dbContext.Sheets.SingleOrDefault(v => v.Id == id);
            if (character == null)
                return HttpNotFound();
            _dbContext.Sheets.Remove(character);
            _dbContext.SaveChanges();
            return RedirectToAction("Index");
        }

        [HttpPost]
        public ActionResult Update(CharacterSheet sheet)
        {
            var videoInDb = _dbContext.Sheets.SingleOrDefault(v => v.Id == sheet.Id);
            if (videoInDb == null)
                return HttpNotFound();
            videoInDb.Name = sheet.Name;
            videoInDb.Class = sheet.Class;
            videoInDb.Level = sheet.Level;
            videoInDb.Race = sheet.Race;
            videoInDb.Public = sheet.Public;
            _dbContext.SaveChanges();
            return RedirectToAction("Index");
        }
    }
}