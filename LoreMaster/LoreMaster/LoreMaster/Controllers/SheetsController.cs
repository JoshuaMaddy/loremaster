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
            _dbContext.Sheets.Add(sheet);
            _dbContext.SaveChanges();
            return RedirectToAction("Index");
        }
    }
}