import boto3
from botocore.exceptions import ClientError

SES_CLIENT = boto3.client('ses', region_name='eu-west-3') 
SENDER = "Luvrane <noreply@luvrane.com>"

def get_html_template(template_type: str, order, customer_name="Client"):
    """
    Retornamos el cuerpo de correo
    """
    #Color
    brand_color = "#000000" 
    
    subjects = {
        "order_received": f"Confirmation de commande #{order.id[:8]} - Luvrane",
        "order_confirmed": "Bonne nouvelle ! Votre commande a été confirmée",
        "order_shipped": "Votre colis est en route!",
        "order_cancelled": "Mise à jour : Commande annulée",
        "new_order_admin": "Nouvelle commande à confirmer"
    }

    # Contenido según el tipo
    if template_type == "order_received":
        title = "Merci pour votre commande !"
        message = "Nous avons bien reçu votre commande. Elle est actuellement en attente de validation par la boutique."
    elif template_type == "order_confirmed":
        title = "Commande Confirmée"
        message = "Votre commande a été validée et est en cours de préparation."
    elif template_type == "order_shipped":
        title = "En route !"
        message = f"Votre colis a été expédié. Numéro de suivi : <b>{order.tracking_number if order.tracking_number else 'Disponible bientôt'}</b>"
    else:
        title = "Mise à jour de votre commande"
        message = f"Le statut de votre commande #{order.id[:8]} a été mis à jour."

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px;">
            <h1 style="color: {brand_color}; text-align: center;">LUVRANE</h1>
            <hr style="border: 0; border-top: 1px solid #eee;">
            <h2 style="color: #444;">{title}</h2>
            <p>Bonjour {customer_name},</p>
            <p>{message}</p>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                <p><b>Résumé de la commande :</b></p>
                <p>ID : #{order.id[:8]}</p>
                <p>Total : <b>{order.total_price} €</b></p>
            </div>
            
            <p style="margin-top: 20px; text-align: center;">
                <a href="https://luvrane.com/account/orders" 
                   style="background-color: {brand_color}; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                   Voir ma commande
                </a>
            </p>
            
            <hr style="border: 0; border-top: 1px solid #eee; margin-top: 30px;">
            <p style="font-size: 12px; color: #999; text-align: center;">
                Ceci est un message automatique, merci de ne pas y répondre.<br>
                &copy; 2026 Luvrane. Tous droits réservés.
            </p>
        </div>
    </body>
    </html>
    """
    return subjects.get(template_type, "Mise à jour Luvrane"), html_content

def send_order_email(to_email: str, template_type: str, order, customer_name="Client"):
    subject, body_html = get_html_template(template_type, order, customer_name)
    
    try:
        SES_CLIENT.send_email(
            Source=SENDER,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Html': {'Data': body_html},
                    'Text': {'Data': f"Commande {order.id}. Visitez notre site para plus de détails."}
                }
            }
        )
    except ClientError as e:
        print(f"Erreur SES: {e.response['Error']['Message']}")
