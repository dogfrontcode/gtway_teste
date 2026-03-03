"""
Application entry point.
"""
import os
from app import create_app, db
from app.models import User, Tenant, Transaction, WebhookAttempt
from app.models.product import Product

# Create Flask application
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    Add database models to Flask shell context.
    Makes it easier to work with models in Flask shell.
    """
    return {
        'db': db,
        'User': User,
        'Tenant': Tenant,
        'Transaction': Transaction,
        'WebhookAttempt': WebhookAttempt,
        'Product': Product
    }


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized successfully!')


@app.cli.command()
def create_admin():
    """Create initial admin user."""
    from app.modules.auth.services import AuthService
    
    email = input('Admin email: ')
    password = input('Admin password: ')
    full_name = input('Admin full name: ')
    
    user, error = AuthService.register(
        email=email,
        password=password,
        full_name=full_name,
        role='admin'
    )
    
    if error:
        print(f'Error creating admin: {error}')
    else:
        print(f'Admin user created successfully: {user.email}')


@app.cli.command()
def seed_db():
    """Seed database with sample data (for development)."""
    from app.modules.auth.services import AuthService
    from app.modules.tenants.services import TenantService
    from decimal import Decimal
    
    print('Seeding database...')
    
    # Create admin user
    admin, error = AuthService.register(
        email='admin@gateway.com',
        password='admin123',
        full_name='Admin User',
        role='admin'
    )
    
    if error and 'already registered' not in error:
        print(f'Error creating admin: {error}')
        return
    
    print('✓ Admin user created')
    
    # Create sample tenant
    tenant_data = {
        'name': 'Sample Store',
        'slug': 'sample-store',
        'legal_name': 'Sample Store LTDA',
        'cnpj': '11222333000181',  # Valid CNPJ for testing
        'email': 'contact@samplestore.com',
        'phone': '+5511999999999',
        'pix_key': 'contact@samplestore.com',
        'bank_provider': 'mock',
        'settings': {
            'primary_color': '#3B82F6',
            'logo_url': 'https://example.com/logo.png'
        }
    }
    
    tenant, error = TenantService.create_tenant(tenant_data)
    
    if error:
        if 'already in use' in error:
            tenant = TenantService.get_tenant_by_slug('sample-store')
            if tenant:
                print('✓ Sample tenant already exists, reusing')
            else:
                print(f'Error creating tenant: {error}')
                return
        else:
            print(f'Error creating tenant: {error}')
            return
    else:
        print(f'✓ Sample tenant created: {tenant.slug}')
    print(f'  API Key: {tenant.api_key}')
    
    # Create tenant user
    tenant_user, error = AuthService.register(
        email='user@samplestore.com',
        password='user123',
        full_name='Store Manager',
        role='tenant_admin',
        tenant_id=tenant.id
    )
    
    if error and 'already registered' not in error:
        print(f'Error creating tenant user: {error}')
    else:
        print('✓ Tenant user created')
    
    # Create sample products
    from app.modules.products.services import ProductService
    from decimal import Decimal
    
    sample_products = [
        {
            'name': 'Curso de Python Completo',
            'description': 'Aprenda Python do zero ao avançado com projetos práticos',
            'sku': 'CURSO-PY-001',
            'price': Decimal('197.00'),
            'category': 'Cursos',
            'image_url': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400',
            'track_stock': False,
        },
        {
            'name': 'Ebook: APIs REST com Flask',
            'description': 'Guia completo para criar APIs profissionais',
            'sku': 'EBOOK-FLASK-001',
            'price': Decimal('49.90'),
            'category': 'Ebooks',
            'track_stock': True,
            'stock_quantity': 1000,
        },
        {
            'name': 'Consultoria 1 hora',
            'description': 'Consultoria técnica individual de 1 hora',
            'sku': 'CONSULT-1H',
            'price': Decimal('250.00'),
            'category': 'Consultoria',
            'track_stock': False,
        },
    ]
    
    for prod_data in sample_products:
        product, error = ProductService.create_product(tenant, prod_data)
        if error:
            if 'already exists' not in error:
                print(f'  Warning: {error}')
        else:
            print(f'  ✓ Product created: {product.name}')
    
    print('\nDatabase seeded successfully!')
    print('\nLogin credentials:')
    print('  Admin: admin@gateway.com / admin123')
    print('  Tenant: user@samplestore.com / user123')


if __name__ == '__main__':
    import os
    import warnings
    from app.utils.logger import log_startup_banner
    
    port = int(os.getenv('PORT', 5001))
    
    # Disable warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', message='.*in-memory storage.*')
    
    # Disable verbose logging
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Print startup banner
    print("\n")
    log_startup_banner()
    print("\n")
    
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=True)
