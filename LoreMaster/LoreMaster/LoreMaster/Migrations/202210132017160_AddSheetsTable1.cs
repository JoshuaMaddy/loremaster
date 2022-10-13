namespace LoreMaster.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class AddSheetsTable1 : DbMigration
    {
        public override void Up()
        {
            AddColumn("dbo.CharacterSheets", "Public", c => c.Boolean(nullable: false));
            AddColumn("dbo.CharacterSheets", "Owner", c => c.String());
        }
        
        public override void Down()
        {
            DropColumn("dbo.CharacterSheets", "Owner");
            DropColumn("dbo.CharacterSheets", "Public");
        }
    }
}
