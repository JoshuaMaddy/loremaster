using Microsoft.Owin;
using Owin;

[assembly: OwinStartupAttribute(typeof(LoreMaster.Startup))]
namespace LoreMaster
{
    public partial class Startup
    {
        public void Configuration(IAppBuilder app)
        {
            ConfigureAuth(app);
        }
    }
}
