using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using System.Web.Optimization;
using System.Web.Routing;
using System.Web.Security;

namespace LoreMaster
{
    public class MvcApplication : System.Web.HttpApplication
    {
        protected void Application_Start()
        {
            AreaRegistration.RegisterAllAreas();
            FilterConfig.RegisterGlobalFilters(GlobalFilters.Filters);
            RouteConfig.RegisterRoutes(RouteTable.Routes);
            BundleConfig.RegisterBundles(BundleTable.Bundles);
        }

        protected void Application_AuthenticateRequest(Object sender, EventArgs e)
        {
            // This is the page
            string cTheFile = HttpContext.Current.Request.Path;

            if (cTheFile.Contains("Sheets") && System.Web.HttpContext.Current.User == null)
            {
                // Check if I am all ready on login page to avoid crash
                if (!cTheFile.EndsWith("Login") && !cTheFile.EndsWith("Register"))
                {
                    // Extract the form's authentication cookie
                    string cookieName = FormsAuthentication.FormsCookieName;
                    HttpCookie authCookie = Context.Request.Cookies[cookieName];

                    // If not logged in
                    if (null == authCookie)
                    // Alternative way of checking:
                    //     if (HttpContext.Current.User == null || HttpContext.Current.User.Identity == null || !HttpContext.Current.User.Identity.IsAuthenticated)
                    {
                        Response.Redirect("/Account/Login", true);
                        Response.End();
                        return;
                    }
                }
            }
        }
    }
}
