<script lang="ts">
	const currentYear = new Date().getFullYear();
</script>

<footer class="footer">
	<div class="footer-content">
		<div class="footer-section">
			<h4 class="footer-title">WSOPTV</h4>
			<p class="footer-text">The world's best poker broadcasts in one place</p>
		</div>

		<div class="footer-section">
			<h4 class="footer-title">Catalogs</h4>
			<ul class="footer-links">
				<li><a href="/catalog/wsop">WSOP</a></li>
				<li><a href="/catalog/hcl">Hustler Casino Live</a></li>
				<li><a href="/catalog/pad">Poker After Dark</a></li>
				<li><a href="/catalog/ggmillions">GG Millions</a></li>
			</ul>
		</div>

		<div class="footer-section">
			<h4 class="footer-title">Help</h4>
			<ul class="footer-links">
				<li><a href="/help">User Guide</a></li>
				<li><a href="/faq">FAQ</a></li>
				<li><a href="/contact">Contact Us</a></li>
			</ul>
		</div>
	</div>

	<div class="footer-bottom">
		<p>&copy; {currentYear} WSOPTV. All rights reserved.</p>
	</div>
</footer>

<style>
	.footer {
		margin-top: auto;
		background: var(--color-surface);
		border-top: 1px solid var(--color-border);
		padding: var(--spacing-xl) 0 var(--spacing-md);
	}

	.footer-content {
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 var(--spacing-md);
		display: grid;
		grid-template-columns: 2fr 1fr 1fr;
		gap: var(--spacing-xl);
	}

	.footer-title {
		font-size: 1rem;
		font-weight: 600;
		margin-bottom: var(--spacing-sm);
		color: var(--color-text);
	}

	.footer-text {
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}

	.footer-links {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.footer-links li {
		margin-bottom: var(--spacing-xs);
	}

	.footer-links a {
		color: var(--color-text-muted);
		text-decoration: none;
		font-size: 0.875rem;
		transition: color 0.2s ease;
	}

	.footer-links a:hover {
		color: var(--color-text);
	}

	.footer-bottom {
		max-width: 1400px;
		margin: var(--spacing-lg) auto 0;
		padding: var(--spacing-md) var(--spacing-md) 0;
		border-top: 1px solid var(--color-border);
		text-align: center;
	}

	.footer-bottom p {
		color: var(--color-text-muted);
		font-size: 0.75rem;
	}

	@media (max-width: 768px) {
		.footer-content {
			grid-template-columns: 1fr;
			gap: var(--spacing-lg);
		}
	}
</style>
