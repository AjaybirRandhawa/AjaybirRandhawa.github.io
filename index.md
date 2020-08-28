# AjaybirRandhawa.github.io
<!DOCTYPE html>
<html>
<head>
    <meta charset = "utf-8" />
    <title> Home</title>
    <link rel="stylesheet" href="styles.css">
</head>    
<body>
    <div class="container">
        <div class="navbar-wrapper">
            <div class="left-column">
                <div class="nav-link-wrapper">
                    <a href="Index.html">Home</a>
                </div>
                <div class="nav-link-wrapper">
                    <a href="about.html">About Me</a>
                </div>
            </div>
            <div class="right-side">
                <div class="name">
                    <div>Ajaybir Singh Randhawa</div>
                </div>
            </div>
        </div>
<!-- The wrappers below can be imagined as on the final product, everything under the nav wrapper is my content wrapper 
containing the items wrapper with the grid and the item wrapper is each singular grid part-->    
        <div class="content-wrapper">
            <div class="portfolio-items-wrapper">
                <div class="portfolio-item-wrapper">
                    <div class="portfolio-img-background" style="background-image:url(images/java.jpg)">
                    </div>
                    <div class="img-text-wrapper">
                        <div class="logo-wrapper">
                            <img src="images/logos/java.png">
                        </div>
                        <div class="subtitle">
                            I started java in my grade 10 computer science class, starting from a simple hello world application to crossword puzzles and space invaders by university.
                        </div>
                    </div>
                </div>
                <div class="portfolio-item-wrapper">
                    <div class="portfolio-img-background" style="background-image:url(images/html5.jpg)">
                    </div>
                    <div class="img-text-wrapper">
                        <div class="logo-wrapper">
                            <img src="images/logos/html52.png">
                        </div>
                        <div class="subtitle">
                            Over the course of the last year, I started learning html5 and was able to create this website.
                        </div>
                    </div>
                </div>
                <div class="portfolio-item-wrapper">
                    <div class="portfolio-img-background" style="background-image:url(images/css.jpg)">
                    </div>
                    <div class="img-text-wrapper">
                        <div class="logo-wrapper">
                            <img src="images/logos/css.png">
                        </div>
                        <div class="subtitle">
                            At the same time as I was learning html5, I learned CSS alongside and implemented it in this website.
                        </div>
                    </div>
                </div>
                <div class="portfolio-item-wrapper">
                    <div class="portfolio-img-background" style="background-image:url(images/Python.jpg)">
                    </div>
                    <div class="img-text-wrapper">
                        <div class="logo-wrapper">
                            <img src="images/logos/python.PNG">
                        </div>
                        <div class="subtitle">
                            At Ryerson I was exposed to python and was able to adapt really quickly due to previous experience with Java.
                        </div>
                    </div>
                </div>
                <div class="portfolio-item-wrapper">
                    <div class="portfolio-img-background" style="background-image:url(images/ryerson.jpg)">
                    </div>
                    <div class="img-text-wrapper">
                        <div class="logo-wrapper">
                            <img src="images/logos/ryerson.png">
                        </div>
                        <div class="subtitle">
                            I enrolled in Ryerson during the fall of 2019 due to its amazing computer science department and close distance to home.
                        </div>
                    </div>
                </div>
                <div class="portfolio-item-wrapper">
                    <div class="portfolio-img-background" style="background-image:url(images/deans\ list.jpg)">
                    </div>
                    <div class="img-text-wrapper">
                        <div class="logo-wrapper">
                            <img src="images/logos/deans list.png">
                        </div>
                        <div class="subtitle">
                            From Peel Technical Skills Challenge in middle school, honour role in highschool to the deans list in university, I have gathered many achievements over my time as a student.
                        </div>
                    </div>
                </div>
                <div class="portfolio-item-wrapper">
                    <div class="portfolio-img-background" style="background-image:url(images/portfolio6.jpg)">
                    </div>
                    <div class="img-text-wrapper">
                        <div class="logo-wrapper">
                            <img src="images/logos/reading.png">
                        </div>
                        <div class="subtitle">
                            I started reading frequently in highschool and  have not stopped since.
                        </div>
                    </div>
                </div>
                <div class="portfolio-item-wrapper">
                    <div class="portfolio-img-background" style="background-image:url(images/ceh.jpg)">
                    </div>
                    <div class="img-text-wrapper">
                        <div class="logo-wrapper">
                            <img src="images/logos/ceh.png">
                        </div>
                        <div class="subtitle">
                            During the summer of 2020, I became interested in cyber security and considered acceptable with scanning, nmaps and ports. I will likely take the CEH examination when possibile.
                        </div>
                    </div>
                </div>
                <div class="portfolio-item-wrapper">
                    <div class="portfolio-img-background" style="background-image:url(images/softskills.jpg)">
                    </div>
                    <div class="img-text-wrapper">
                        <div class="logo-wrapper">
                            <img src="images/logos/download.png">
                        </div>
                        <div class="subtitle">
                            Hardworking, cooperative and leadership are attributes that describe me best.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
<script>
    const portfolioItems = document.querySelectorAll('.portfolio-item-wrapper');
    portfolioItems.forEach(portfolioItem => {
        portfolioItem.addEventListener('mouseover', () => {
            console.log(portfolioItem.childNodes[1].classList);
            portfolioItem.childNodes[1].classList.add('img-darken');
        });
        portfolioItem.addEventListener('mouseout', () => {
            portfolioItem.childNodes[1].classList.remove('img-darken');
        });
    });    
</script>
</html>
