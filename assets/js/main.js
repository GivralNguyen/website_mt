/*
	Dimension by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

(function($) {
	'use strict';

	var $window = $(window),
		$body = $('body'),
		$wrapper = $('#wrapper'),
		$header = $('#header'),
		$main = $('#main'),
		$articles = $main.children('article'),
		$navLinks = $header.find('nav a[href^="#"]'),
		homeTitle = document.title,
		activeArticle = null;

	if (typeof breakpoints === 'function') {
		breakpoints({
			xlarge: ['1281px', '1680px'],
			large: ['981px', '1280px'],
			medium: ['737px', '980px'],
			small: ['481px', '736px'],
			xsmall: ['361px', '480px'],
			xxsmall: [null, '360px']
		});
	}

	function navigationLink(article) {
		return $navLinks.filter(function() {
			return this.getAttribute('href') === '#' + article.id;
		}).first();
	}

	function sectionName(article) {
		return $.trim(navigationLink(article).text()) || article.getAttribute('aria-label') || homeTitle;
	}

	function focusContent(target) {
		// Headings and other fragment targets also need to accept programmatic focus.
		if (!target.hasAttribute('tabindex') && !$(target).is('a[href], button, input, select, textarea')) {
			target.setAttribute('tabindex', '-1');
		}
		target.focus({preventScroll: true});
		target.scrollIntoView({block: 'start'});
	}

	function showArticle(article, initial, target) {
		// Update visibility and focus together. Delayed hide/show callbacks can leave
		// focus in a hidden section when navigation happens during a transition.
		$articles.not(article).removeClass('active').hide().prop('hidden', true);
		$header.hide().prop('hidden', true);
		$body.addClass('is-article-visible');
		$main.prop('hidden', false).show();
		$(article).prop('hidden', false).show().addClass('active');
		activeArticle = article;
		$navLinks.removeAttr('aria-current');
		navigationLink(article).attr('aria-current', 'page');
		document.title = sectionName(article) + ' | ' + homeTitle;

		if (!initial || target !== article) {
			focusContent(target || article);
		} else {
			window.scrollTo(0, 0);
		}
		$window.triggerHandler('resize.flexbox-fix');
	}

	function showHome(initial) {
		var previousArticle = activeArticle;
		$articles.removeClass('active').hide().prop('hidden', true);
		$main.hide().prop('hidden', true);
		$body.removeClass('is-article-visible');
		$header.prop('hidden', false).show();
		$navLinks.removeAttr('aria-current');
		document.title = homeTitle;
		activeArticle = null;

		if (!initial && previousArticle) {
			// Let the browser scroll the restored control into view, even when the
			// home page is taller than the viewport at high zoom or on a phone.
			var link = navigationLink(previousArticle)[0];
			if (link) link.focus();
		}
		$window.triggerHandler('resize.flexbox-fix');
	}

	function fragmentTarget() {
		var id = location.hash.slice(1);
		try {
			id = decodeURIComponent(id);
		} catch (error) {
			// A malformed fragment must not break all subsequent navigation.
			return null;
		}
		return document.getElementById(id);
	}

	function route(initial) {
		var target = fragmentTarget(),
			article = target && $(target).closest('#main > article')[0];

		if (article) {
			showArticle(article, initial, target);
		} else if (target === $main[0]) {
			// The main landmark is hidden on the home screen; expose its first
			// section before moving focus there for the skip link.
			if ($articles.length) showArticle(activeArticle || $articles[0], false, activeArticle || $articles[0]);
		} else {
			showHome(initial);
			if (target && !initial) focusContent(target);
		}
	}

	function closeArticle() {
		if (!activeArticle) return;
		history.pushState(null, '', location.pathname + location.search);
		showHome(false);
	}

	$articles.each(function() {
		var article = this;
		$(article).attr('tabindex', '-1');
		if (!article.hasAttribute('aria-label') && !article.hasAttribute('aria-labelledby')) {
			article.setAttribute('aria-label', sectionName(article));
		}

		// A native button supports keyboard, touch, and assistive technology
		// activation without a second, synthetic keyboard implementation.
		$('<button type="button" class="close">Close</button>')
			.attr('aria-label', 'Close ' + sectionName(article) + ' and return to home')
			.prependTo(article)
			.on('click', closeArticle);
	});

	$('.skip-link').on('click', function(event) {
		event.preventDefault();
		var article = activeArticle || $articles[0];
		if (!article) return;
		if (!activeArticle) history.pushState(null, '', '#' + article.id);
		showArticle(article, false, article);
	});

	// A repeated link to the current fragment still brings its content into view.
	$navLinks.on('click', function(event) {
		if (!event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && this.hash === location.hash) {
			event.preventDefault();
			route(false);
		}
	});

	$body.on('click', function(event) {
		if (event.target === $body[0] || event.target === $wrapper[0]) closeArticle();
	});

	$window.on('keydown', function(event) {
		if (event.key === 'Escape' && activeArticle && !event.defaultPrevented) {
			event.preventDefault();
			closeArticle();
		}
	});
	$window.on('hashchange', function() { route(false); });

	// Keep accessible names intact, including image alternative text, when
	// adding the new-tab notice to links without an explicit accessible label.
	$('a[target="_blank"]').each(function() {
		var label = this.getAttribute('aria-label');
		if (/opens in new tab/i.test(label || this.textContent)) return;
		if (label) {
			this.setAttribute('aria-label', label + ' (opens in new tab)');
		} else {
			$('<span class="sr-only"> (opens in new tab)</span>').appendTo(this);
		}
	});

	// Retain the template's layout correction without making navigation depend
	// on the optional browser-detection script loading successfully.
	if (typeof browser !== 'undefined' && browser.name === 'ie') {
		$window.on('resize.flexbox-fix', function() {
			$wrapper.css('height', $wrapper.prop('scrollHeight') > $window.height() ? 'auto' : '100vh');
		});
	}

	$body.removeClass('is-preload');
	route(true);
})(jQuery);
