from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CategoryItem, User

# Create database and create a shortcut for easier to update database
engine = create_engine('sqlite:///catalogs.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = User(name="im Robot", email="saliha.al@gmail.com")
session.add(User1)
session.commit()


category1 = Catalog(user_id=1, name="Gabriel Garcia Marquez")
session.add(category1)
session.commit()


category2 = Catalog(user_id=1, name="Agatha Christie")
session.add(category2)
session.commit()


category3 = Catalog(user_id=1, name="William Shakespeare")
session.add(category3)
session.commit()


category4 = Catalog(user_id=1, name="Margaret Mitchell")
session.add(category4)
session.commit()


categoryItem1 = CategoryItem(
    user_id=1,
    name="One Hundred Years of Solitude",
    description="""The brilliant, bestselling,
    landmark novel that tells the story of the
    Buendia family,and chronicles the irreconcilable
    conflict between the desire for
    solitude and the need for love-in rich,imaginative
    prose that has come to define an
    entire genre known as magical realism""", categories=category1)
session.add(categoryItem1)
session.commit()

categoryItem1 = CategoryItem(
    user_id=1,
    name="Love in the Time of Cholera",
    description="""In their youth, Florentino Ariza and
    Fermina Daza fall passionately in love.
    When Fermina eventually chooses to marry a wealthy,
    well-born doctor, Florentino is heartbroken,
    but he is a romantic. As he rises in his business career he
    whiles away the years in 622 affairs--yet
    he reserves his heart for Fermina.
    Her husband dies at last, and Florentino purposefully attends
    the funeral. Fifty years, nine months,
    and four days after he first declared his love
    for Fermina, he will do so again""",
    categories=category1)
session.add(categoryItem1)
session.commit()

categoryItem1 = CategoryItem(
    user_id=1, name="Murder at the Vicarage",
    description="""Murder at the Vicarage marks the debut of
    Agatha Christie's unflappable
    and much beloved female detective, Miss Jane Marple.
    With her gift for sniffing out the malevolent side of
    human nature, Miss Marple is led on her first case to a crime scene at
    the local vicarage.Colonel Protheroe, the magistrate whom everyone in
    town hates,has been shot through the head.No one heard the shot. There
    are no leads.Yet, everyone surrounding the vicarage seems to have a reason
    to want the Colonel dead.It is a race against the clock as Miss Marple
    sets out on the twistedtrail of the mysterious killerwithout so much as
    a bit of help from the local police.""", categories=category2)
session.add(categoryItem1)
session.commit()

categoryItem1 = CategoryItem(
    user_id=1,
    name="Evil Under the Sun",
    description="""Set at the Jolly Roger, a posh vacation resort for the rich and
    famous on the southern coast of England,Evil Under the Sun is one of
    Agatha Christie's most intriguing mysteries.When a gorgeous young bride
    is brutallystrangled to death on the beach,only Hercule Poirot can sift
    throughthe secrets thatshroud each of the guestsand unravel the macabre
    mystery at this playground by the sea.""", categories=category2)
session.add(categoryItem1)
session.commit()

categoryItem1 = CategoryItem(
    user_id=1, name="Twelfth Night",
    description="""Set in a topsy-turvy world like a holiday revel,
    this comedy devises a romantic plot around separated twins misplaced
    passions,and mistaken identity. Juxtaposed to it is the satirical
    story of a self-deluded stewardwho dreams of becoming Count Malvolioonly
    to receive his comeuppance at the hands of the merrymakershe wishes to
    suppress. The two plots combine to create a farce touched with melancholy,
    mixed throughout with seductively beautiful explorations on the themes of
    love and time,and the play ends, not with laughter,but with a clown's
    sad song.""", categories=category3)
session.add(categoryItem1)
session.commit()

categoryItem1 = CategoryItem(
    user_id=1,
    name="As You Like It",
    description="""As You Like It follows its heroine Rosalind as she flees
    persecution in her uncle's court, accompanied by her cousin Celia and
    Touchstone the court jester, to find safety and, eventually, love, in the
    Forest of Arden. Historically, critical response has varied,with some
    criticsfinding the work of lesser quality than other Shakespearean works
    and somefinding the play a work of great merit. The play features one of
    Shakespeare'smost famous andoft-quoted speeches,"All the world's a stage",
    and is the originof the phrase "too much of a good thing".The play remains
    a favourite amongaudiencesand has been adapted for radio, film,and musical
    theatre.""", categories=category3)
session.add(categoryItem1)
session.commit()

categoryItem1 = CategoryItem(
    user_id=1, name="Gone with the Wind",
    description="""Gone with the Wind is a novel written by Margaret Mitchell,
    first published in 1936. The story is set in Clayton County, Georgia,
    and Atlanta during the American Civil War and Reconstruction era. It
    depicts the struggles of young Scarlett O'Hara,the daughter of a
    well-to-doplantation owner, who must use every means at her disposal
    of the povertyshefinds herself in after Sherman's March to the Sea.
    A historical novel, the story is a Bildungsroman or coming-of-age
    story,with the title takenfrom a poem written byErnest Dowson.""",
    categories=category4)
session.add(categoryItem1)
session.commit()


print "added category items!"
