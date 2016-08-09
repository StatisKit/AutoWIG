<html class="no-js" lang="en"> <!--<![endif]-->
<head>
  <meta charset="utf-8">
  
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <title>AutoWIG: Automatic Wrapper and Interface Generator &#8212; AutoWIG 0.1.0 documentation</title>
  

  
  

  

  
  
    

  

  
  

  
    <link rel="stylesheet" href="https://media.readthedocs.org/css/sphinx_rtd_theme.css" type="text/css">
  

  
    <link rel="top" title="AutoWIG 0.1.0 documentation" href="http://autowig.readthedocs.io/en/latest/">
        <link rel="next" title="Installation from sources" href="http://autowig.readthedocs.io/en/latest/install.html"> 

  
  <script src="http://autowig.readthedocs.io/en/latest/_static/js/modernizr.min.js"></script>


<!-- RTD Extra Head -->

<!-- 
Always link to the latest version, as canonical.
http://docs.readthedocs.org/en/latest/canonical.html
-->
<link rel="canonical" href="http://autowig.readthedocs.io/en/latest/">

<link rel="stylesheet" href="https://media.readthedocs.org/css/readthedocs-doc-embed.css" type="text/css">

<script type="text/javascript" src="http://autowig.readthedocs.io/en/latest/_static/readthedocs-data.js"></script>

<!-- Add page-specific data, which must exist in the page js, not global -->
<script type="text/javascript">
READTHEDOCS_DATA['page'] = 'index'
</script>

<script type="text/javascript" src="http://autowig.readthedocs.io/en/latest/_static/readthedocs-dynamic-include.js"></script>

<!-- end RTD <extrahead> --></head>

<body class="wy-body-for-nav" role="document">

  <div class="wy-grid-for-nav">

    
    <nav data-toggle="wy-nav-shift" class="wy-nav-side">
      <div class="wy-side-scroll">
        <div class="wy-side-nav-search">
          

          
            <a href="http://autowig.readthedocs.io/en/latest/" class="icon icon-home"> AutoWIG
          

          
          </a>

          
            
            
            
              <div class="version">
                latest
              </div>
            
          

          
<div role="search">
  <form id="rtd-search-form" class="wy-form" action="http://autowig.readthedocs.io/en/latest/search.html" method="get">
    <input type="text" name="q" placeholder="Search docs">
    <input type="hidden" name="check_keywords" value="yes">
    <input type="hidden" name="area" value="default">
  </form>
</div>

          
        </div>

        <div class="wy-menu wy-menu-vertical" data-spy="affix" role="navigation" aria-label="main navigation">
          
            
            
                <ul>
<li class="toctree-l1"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/install.html">Installation from sources</a></li>
<li class="toctree-l1"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/motivating_example.html">Motivating example</a></li>
<li class="toctree-l1"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/methodology.html">Methodology</a></li>
</ul>

            
          
        </div>
      </div>
    </nav>

    <section data-toggle="wy-nav-shift" class="wy-nav-content-wrap">

      
      <nav class="wy-nav-top" role="navigation" aria-label="top navigation">
        <i data-toggle="wy-nav-top" class="fa fa-bars"></i>
        <a href="http://autowig.readthedocs.io/en/latest/">AutoWIG</a>
      </nav>


      
      <div class="wy-nav-content">
        <div class="rst-content">
          





<div role="navigation" aria-label="breadcrumbs navigation">
  <ul class="wy-breadcrumbs">
    <li><a href="http://autowig.readthedocs.io/en/latest/">Docs</a> &#187;</li>
      
    <li>AutoWIG: Automatic Wrapper and Interface Generator</li>
      <li class="wy-breadcrumbs-aside">
        
          
            <a href="https://github.com/VirtualPlants/AutoWIG/blob/master/doc/index.rst" class="fa fa-github"> Edit on GitHub</a>
          
        
      </li>
  </ul>
  <hr>
</div>
          <div role="main" class="document" itemscope="itemscope" itemtype="http://schema.org/Article">
           <div itemprop="articleBody">
            
  <span class="target" id="module-autowig"><span id="autowig"></span></span><div class="section" id="autowig-automatic-wrapper-and-interface-generator">
<h1>AutoWIG: Automatic Wrapper and Interface Generator<a class="headerlink" href="http://autowig.readthedocs.io/en/latest/#autowig-automatic-wrapper-and-interface-generator" title="Permalink to this headline">&#182;</a></h1>
<p>High-level programming languages, like <em>Python</em> and <em>R</em>, are popular among scientists.
They tend to be concise and readable, leading to a rapid development cycle, but suffer from performance drawback compare to compiled language.
However, these languages allow to interface <em>C</em>, <em>C++</em> and <em>Fortran</em> code.
By this way, most of the scientific packages incorporate compiled scientific libraries to both speed up the code and reuse legacy libraries.
While several semi-automatic solutions and tools exist to wrap these compiled libraries, the process of wrapping a large library is cumbersome and time consuming.
In this paper, we introduce <strong>AutoWIG</strong>, a <em>Python</em> library that wraps automatically <em>C++</em> libraries into high-level languages.
Our solution consists in parsing <em>C++</em>  code using <strong>LLVM</strong>/<strong>CLang</strong> technology and generating the wrappers using the <strong>Mako</strong> templating engine.
Our approach is automatic, extensible, and can scale from simple <em>C++</em> libraries to very complex ones, composed of thousands of classes or using modern meta-programming constructs.
The usage and extension of <strong>AutoWIG</strong> is also illustrated on a set of statistical libraries.</p>
<div class="sidebar">
<p class="first sidebar-title">Summary</p>
<table class="last docutils field-list" frame="void" rules="none">
<col class="field-name">
<col class="field-body">
<tbody valign="top">
<tr class="field-odd field"><th class="field-name">Version:</th><td class="field-body">0.1.0</td>
</tr>
<tr class="field-even field"><th class="field-name">Release:</th><td class="field-body">0.1.0</td>
</tr>
<tr class="field-odd field"><th class="field-name">Date:</th><td class="field-body">June 30, 2016</td>
</tr>
<tr class="field-even field"><th class="field-name">Status:</th><td class="field-body"><a class="reference external" href="https://travis-ci.org/VirtualPlants/AutoWIG"><img alt="Travis" src="https://travis-ci.org/VirtualPlants/AutoWIG.svg?branch=master"></a> <a class="reference external" href="https://coveralls.io/github/VirtualPlants/AutoWIG?branch=master"><img alt="Coveralls" src="https://coveralls.io/repos/github/VirtualPlants/AutoWIG/badge.svg?branch=master"></a> <a class="reference external" href="https://landscape.io/github/VirtualPlants/AutoWIG/master"><img alt="Landscape" src="https://landscape.io/github/VirtualPlants/AutoWIG/master/landscape.svg?style=flat"></a> <a class="reference external" href="http://AutoWIG.readthedocs.io/en/latest"><img alt="Read the Docs" src="https://readthedocs.org/projects/AutoWIG/badge/?version=latest"></a></td>
</tr>
<tr class="field-odd field"><th class="field-name">Author:</th><td class="field-body">See <a class="reference internal" href="http://autowig.readthedocs.io/en/latest/#authors">Authors</a> section</td>
</tr>
</tbody>
</table>
</div>
<div class="section" id="documentation">
<h2>Documentation<a class="headerlink" href="http://autowig.readthedocs.io/en/latest/#documentation" title="Permalink to this headline">&#182;</a></h2>
<div class="toctree-wrapper compound">
<ul>
<li class="toctree-l1"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/install.html">Installation from sources</a><ul>
<li class="toctree-l2"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/install.html#requirements">Requirements</a></li>
</ul>
</li>
<li class="toctree-l1"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/motivating_example.html">Motivating example</a></li>
<li class="toctree-l1"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/methodology.html">Methodology</a><ul>
<li class="toctree-l2"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/methodology.html#an-interactive-workflow">An interactive workflow</a></li>
<li class="toctree-l2"><a class="reference internal" href="http://autowig.readthedocs.io/en/latest/methodology.html#integrated-workflows">Integrated workflows</a></li>
</ul>
</li>
</ul>
</div>
</div>
<div class="section" id="authors">
<h2>Authors<a class="headerlink" href="http://autowig.readthedocs.io/en/latest/#authors" title="Permalink to this headline">&#182;</a></h2>
</div>
<div class="section" id="license">
<h2>License<a class="headerlink" href="http://autowig.readthedocs.io/en/latest/#license" title="Permalink to this headline">&#182;</a></h2>
<p><strong>AutoWIG</strong> is distributed under the <a class="reference external" href="http://autowig.readthedocs.io/en/latest/license.html">CeCILL-C license</a>.</p>
<div class="admonition note">
<p class="first admonition-title">Note</p>
<p class="last"><a class="reference external" href="http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html">Cecill-C</a>
license is a LGPL compatible license.</p>
</div>
</div>
</div>


           </div>
          </div>
          <footer>
  
    <div class="rst-footer-buttons" role="navigation" aria-label="footer navigation">
      
        <a href="http://autowig.readthedocs.io/en/latest/install.html" class="btn btn-neutral float-right" title="Installation from sources" accesskey="n">Next <span class="fa fa-arrow-circle-right"></span></a>
      
      
    </div>
  

  <hr>

  <div role="contentinfo">
    <p>
        &#169; Copyright 2016, Pierre Fernique &amp; Christophe Pradal.
      
        <span class="commit">
          Revision <code>45767086</code>.
        </span>
      

    </p>
  </div>
  Built with <a href="http://sphinx-doc.org/">Sphinx</a> using a <a href="https://github.com/snide/sphinx_rtd_theme">theme</a> provided by <a href="https://readthedocs.org">Read the Docs</a>. 

</footer>

        </div>
      </div>

    </section>

  </div>
  

  <div class="rst-versions" data-toggle="rst-versions" role="note" aria-label="versions">
    <span class="rst-current-version" data-toggle="rst-current-version">
      <span class="fa fa-book"> Read the Docs</span>
      v: latest
      <span class="fa fa-caret-down"></span>
    </span>
    <div class="rst-other-versions">
      <dl>
        <dt>Versions</dt>
        
          <dd><a href="http://autowig.readthedocs.io/en/latest/">latest</a></dd>
        
      </dl>
      <dl>
        <dt>Downloads</dt>
        
      </dl>
      <dl>
        <dt>On Read the Docs</dt>
          <dd>
            <a href="http://readthedocs.org/projects/autowig/?fromdocs=autowig">Project Home</a>
          </dd>
          <dd>
            <a href="http://readthedocs.org/builds/autowig/?fromdocs=autowig">Builds</a>
          </dd>
      </dl>
      <hr>
      Free document hosting provided by <a href="http://www.readthedocs.org">Read the Docs</a>.

    </div>
  </div>



  

    <script type="text/javascript">
        var DOCUMENTATION_OPTIONS = {
            URL_ROOT:'./',
            VERSION:'0.1.0',
            COLLAPSE_INDEX:false,
            FILE_SUFFIX:'.html',
            HAS_SOURCE:  true
        };
    </script>
      <script type="text/javascript" src="https://media.readthedocs.org/javascript/jquery/jquery-2.0.3.min.js"></script>
      <script type="text/javascript" src="https://media.readthedocs.org/javascript/jquery/jquery-migrate-1.2.1.min.js"></script>
      <script type="text/javascript" src="https://media.readthedocs.org/javascript/underscore.js"></script>
      <script type="text/javascript" src="https://media.readthedocs.org/javascript/doctools.js"></script>
      <script type="text/javascript" src="https://media.readthedocs.org/javascript/readthedocs-doc-embed.js"></script>
      <script type="text/javascript" src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>

  

  
  

  
  
  <script type="text/javascript">
      jQuery(function () {
          SphinxRtdTheme.StickyNav.enable();
      });
  </script>
   

</body>
</html>
