# Documentation
   * [v0.6.1] (http://pynastran-git.readthedocs.org/en/v0.6/index.html)
   * v0.7
   * [Master/Trunk](http://pynastran-git.readthedocs.org/en/latest/index.html)

Also, check out the [Wiki](https://github.com/SteveDoyle2/pynastran/wiki) for more detailed information.

<!--- http://pynastran-git.readthedocs.org/en/v0.6/index.html      doesnt work???...isn't this "stable" -->
<!--- http://pynastran-git.readthedocs.org/en/stable/index.html    is not used yet...will be v0.7 later? -->
<!--- http://stevedoyle2.github.io/pyNastran/ >

# News


## pyNastran has Moved (3/12/2015)
Google Code is  [closing down](http://google-opensource.blogspot.com/2015/03/farewell-to-google-code.html)
on January 25, 2016 and as such pyNastran is moving to [github](https://github.com/SteveDoyle2/pynastran).
New commits will now be made on github.  The wiki is currently in the process of being migrated to github.

Git is harder to get used to, but gets rid of a lot of the pain of branching and merging.  Also,
a lot of useful tools (e.g. readthedocs) just work with Github that don't work well with
other hosting services.  Checkouts and updates are also many, many fimes faster.




## pyNastran v0.7

The long awaited new release (v0.7) is coming soon.  It is a major update.
The target is sometime within the next month.  Testing is nearly done, but there are a
few cleanup tasks to do.

Some of the improvements include:
 * OP2
   * superelement support
   * vectorized support (uses much less memory; Element Forces not vectorized yet)
   * additional results (e.g. grid point weight, eigenvalues)
   * `PARAM,POST,-2` support
 * F06
   * improved F06 reader (the OP2 reader is still better)
 * BDF
   * 20 new BDF cards
   * large field format and double precision writing
 * GUI
   * much improved GUI with transient support (real only), a results sidebar, logging, and scripting support
 * Other
   * additional readers/converters to/from various other formats (e.g. STL, Cart3d, Panair) as well as GUI support
   * Python 2/3 support with a single code base
   * autogenerated online documentation for pyNastran using [readthedocs](https://rwww.readthedocs.org) and [Sphinx](http://sphinx-doc.org/)

As always there are many bug fixes and many new tests.

Additionally, there have also been many API changes.  It's a frustrating step, but pyNastran is adopting PEP-8.
Where possible, old methods will be maintained until v0.8, but that is not always possible.  If an old method is not supported and hadn't previouly been deprecated, make a ticket/issue and if it can be supported, it will be added back.

## Download Page
Google Code no longer supports new downloads.
As such, the download page will now be located at [Sourceforge](https://sourceforge.net/projects/pynastran/files/?source=navbar).  The much improved dev version of the [GUI](https://github.com/SteveDoyle2/pynastran/wiki/GUI) is located there.
v0.6.1 and earlier releases will still be located at Google Code (at least for now).

## Version 0.6.1 has been released
**Version 0.6** improves BDF reading.  The reader is more robust and also requires proper BDF field formatting (e.g. a integer field can't be a float).  Additionally, cards also have a comment() method.

Marcin Gąsiorek participated in the latest pyNastran under the European Space Agency's (ESA) "Summer of Code In Space" [SOCIS](http://sophia.estec.esa.int/socis2012/?q=node/13) program.  The program provides a stipend to students to work on open-source projects.
He did a great job of simplifying code and creating nicer documentation.

Also, if anyone knows how to setup a project with readthedocs.org, we can get pyNastran documentation setup online.

## Additional Info
Note the wiki refers to the most current released version (v0.6.1) unless noted.

If anyone makes any specific requests I'll try to incorporate them.  They need to be specific, such as read these cards from the BDF, read these results from this OP2, or write these results to an OP2.  <b>Any sample problems that you have (to test the software with) would be appreciated.  I need small examples that are comprehensive that I can add as demo problems.</b>

Check out the following if you're interested to see what's being worked on:
 * <A href="https://github.com/SteveDoyle2/pynastran/blob/master/releaseNotes.txt">Release Notes</A>
