using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace LoreMaster.Controllers
{
    public class SheetsController : Controller
    {
        // GET: Sheets
        public ActionResult Index()
        {
            return View();
        }
    }
}