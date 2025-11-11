import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Conexión 
CADENA_ATLAS = "mongodb+srv://a368027_db_user:GGGGP66SFFThwerU@proyecto2bdii.tjc6oij.mongodb.net/Proyecto2BDII?retryWrites=true&w=majority"

try:
    client = MongoClient(CADENA_ATLAS)  #contraseña mongoAtlas: GGGGP66SFFThwerU
    db = client["Proyecto2BDII"]
    
    users_col = db["users"]
    categories_col = db["categories"]
    tags_col = db["tags"]
    articles_col = db["articles"]
    comments_col = db["comments"]
    
    client.server_info()
except pymongo.errors.ConnectionFailure as e:
    print(f"Error: No se pudo conectar a MongoDB")
    print(e)
    exit()


#Crear / Create

def registrar_usuario(nombre, email, password):
    if users_col.find_one({"email": email}):
        return "El email registrado."

    if users_col.find_one({"name": nombre}):
        return "Nombre de usuario ya está en uso."

    nuevo_usuario = {
        "name": nombre,
        "email": email,
        "password": password,
        "role": "user"  
    }
    result = users_col.insert_one(nuevo_usuario)
    
    if result.inserted_id:
        return result.inserted_id 
    else:
        return "No se pudo registrar al usuario."

def agregar_comentario(article_id_str, user_id_str, texto_comentario):   
    try:
        obj_article_id = ObjectId(article_id_str)
        obj_user_id = ObjectId(user_id_str)
    except Exception as e:
        print(f" {e}")
        return " "

    # Si el articulo existe
    articulo = articles_col.find_one({"_id": obj_article_id})
    if not articulo:
        return "No se encontró el artículo."
    
    nuevo_comentario = {
        "text": texto_comentario,
        "article_id": obj_article_id,
        "user_id": obj_user_id,
        "date": datetime.now()  
    }
    result = comments_col.insert_one(nuevo_comentario)
    return result.inserted_id

def crear_articulo(user_id, titulo, texto, ids_categorias, ids_tags):   
   #ObjectId
    try:
        obj_user_id = ObjectId(user_id)
        obj_cats = [ObjectId(cat_id) for cat_id in ids_categorias]
        obj_tags = [ObjectId(tag_id) for tag_id in ids_tags]
    except Exception as e:
        print(f" {e}")
        return " "

    nuevo_articulo = {
        "title": titulo,
        "date": datetime.now(),
        "text": texto,
        "user_id": obj_user_id,
        "categories": obj_cats,
        "tags": obj_tags
    }
    
    result = articles_col.insert_one(nuevo_articulo)
    return result.inserted_id

def crear_categoria(nombre):   
    # si ya existe
    if categories_col.find_one({"name": nombre}):
        return "Esa categoría ya existe"
    
    nueva_cat = {"name": nombre}
    result = categories_col.insert_one(nueva_cat)
    
    if result.inserted_id:
        return result.inserted_id
    else:
        return "No se pudo crear la categoría."

def crear_tag(nombre): 
    #si ya existe 
    if tags_col.find_one({"name": nombre}):
        return "Error: Ese tag ya existe"
    
    nuevo_tag = {"name": nombre}
    result = tags_col.insert_one(nuevo_tag)
    
    if result.inserted_id:
        return result.inserted_id
    else:
        return "Error: No se pudo crear el tag."
    


#Mostrar / Read

def iniciar_sesion(nombre, email, password): 
    # Busca usuario con los tres campos en la variable users_cpl
    usuario = users_col.find_one({
        "name": nombre,
        "email": email,
        "password": password
    })
    
    return usuario

def Articulos_blog():
    
    pipeline = [
        # 1. Busca la info del autor del artículo (obtener nombre de usuario)
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "autor_info"}},
        # 2. Busca la info de las categorías
        {"$lookup": {"from": "categories", "localField": "categories", "foreignField": "_id", "as": "categorias_info"}},
        # 3. Busca la info de los tags
        {"$lookup": {"from": "tags", "localField": "tags", "foreignField": "_id", "as": "tags_info"}},
        # 4. Descomprime la información del autor
        {"$unwind": {"path": "$autor_info", "preserveNullAndEmptyArrays": True}},
        {
           # proyecta / Limpia y renombra los campos
            "$project": {
                "_id": 1,
                "titulo": "$title",
                "fecha": "$date",
                "texto": "$text",
                "autor_nombre": "$autor_info.name",
                "categorias": "$categorias_info.name", 
                "tags": "$tags_info.name"
            }
        },
        # 6. Ordena por fecha
        {"$sort": {"fecha": -1}} 
    ]
    
    articulos = list(articles_col.aggregate(pipeline))
    return articulos

def obtener_todos_comentarios():
    """
    Trae todos los comentarios con la info del autor y del artículo.
    (La 'R' de CRUD)
    """
    pipeline = [
        # 1. Busca la info del autor
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "autor_info"}},
        # 2. Busca la info del artículo
        {"$lookup": {"from": "articles", "localField": "article_id", "foreignField": "_id", "as": "articulo_info"}},
        # 3. Descomprime arrays a que sean objetos
        {"$unwind": {"path": "$autor_info", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$articulo_info", "preserveNullAndEmptyArrays": True}},
        {
            # 4. Proyecta solo lo que se necesita de la tabla 
            "$project": {
                "_id": 1,
                "texto_comentario": "$text",
                "fecha": "$date",
                "autor_nombre": "$autor_info.name",
                "articulo_titulo": "$articulo_info.title"
            }
        },
        # 5. Ordena por fecha 
        {"$sort": {"fecha": -1}}
    ]
    
    comentarios = list(comments_col.aggregate(pipeline))

    for comentario in comentarios:
        fecha = comentario.get('fecha')
        if isinstance(fecha, str):
            # Si la fecha es un texto 
            try:
                fecha_limpia_str = fecha.split('.')[0].replace('Z', '')
                comentario['fecha'] = datetime.strptime(fecha_limpia_str, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                comentario['fecha'] = None
    return comentarios

def obtener_todas_categorias():
    return list(categories_col.find())

def obtener_todos_tags():
    return list(tags_col.find())

def obtener_todos_usuarios():
    # .sort("name", 1) para ordenarlos alfabéticamente por nombre
    usuarios = list(users_col.find().sort("name", 1))
    return usuarios

def obtener_articulo_por_id(article_id_str):
    """
    Busca un solo artículo por su ID.
    se usa indirectamente para la opcion de  "Editar".
    """
    try:
        obj_article_id = ObjectId(article_id_str)
    except Exception as e:
        print(f"Error al convertir ID de artículo: {e}")
        return None

    # Busca el artículo.
    articulo = articles_col.find_one({"_id": obj_article_id})
    
    # convuerte los IDs de categorías y tags a strings
    if articulo:
        articulo['categories'] = [str(cat_id) for cat_id in articulo.get('categories', [])]
        articulo['tags'] = [str(tag_id) for tag_id in articulo.get('tags', [])]

    return articulo

def obtener_categoria_por_id(cat_id_str):
    #busca una categoría por su ID para editarla
    try:
        obj_cat_id = ObjectId(cat_id_str)
    except Exception as e:
        print(f"Error al convertir ID de categoría: {e}")
        return None
    
    return categories_col.find_one({"_id": obj_cat_id})

def obtener_tag_por_id(tag_id_str):
    #busca una tag por su ID para editarla
    try:
        obj_tag_id = ObjectId(tag_id_str)
    except Exception as e:
        print(f"Error al convertir ID de tag: {e}")
        return None
    
    return tags_col.find_one({"_id": obj_tag_id})

def obtener_comentario_por_id(comment_id_str):
    #busca una tag por su ID para editarla
    try:
        obj_comment_id = ObjectId(comment_id_str)
    except Exception as e:
        print(f"Error al convertir ID de comentario: {e}")
        return None
    
    return comments_col.find_one({"_id": obj_comment_id})

#Editar/Update

def editar_articulo(article_id_str, titulo, texto, ids_categorias, ids_tags):
    # IDs de string a ObjectId
    try:
        obj_article_id = ObjectId(article_id_str)
        obj_cats = [ObjectId(cat_id) for cat_id in ids_categorias]
        obj_tags = [ObjectId(tag_id) for tag_id in ids_tags]
    except Exception as e:
        print(f" {e}")
        return False

    filtro = {"_id": obj_article_id} # a quién vamos a buscar
    actualizacion = { # $set actualiza solo estos campos especificados
        "$set": {
            "title": titulo,
            "text": texto,
            "categories": obj_cats,
            "tags": obj_tags
            # No fecha ni user_id
        }}
    try:
        result = articles_col.update_one(filtro, actualizacion)   
        # si se modificó algo
        # result.modified_count significa que encontró y actualizó.
        # result.matched_count y modified_count significa que lo encontró, pero los datos eran idénticos y no hubo necesidad de cambiar.
        
        if result.modified_count == 1 or result.matched_count == 1:
            return True
        else: return False            
    except Exception as e:
        print(f"Error {e}")
        return False

def editar_comentario(comment_id_str, nuevo_texto):  
    try:
        obj_comment_id = ObjectId(comment_id_str)
    except Exception as e:
        print(f"Error al convertir ID: {e}")
        return False

    # filtro de id 
    filtro = {"_id": obj_comment_id}

    # El campo text según función 'agregar_comentario'
    actualizacion = {"$set": {"text": nuevo_texto}}
    
    try:
        # comments_col
        result = comments_col.update_one(filtro, actualizacion)
        if result.modified_count == 1 or result.matched_count == 1:
            return True
        else:
            return False # No lo encontró
    except Exception as e:
        print(f"Error al editar comentario: {e}")
        return False

def editar_categoria(cat_id_str, nuevo_nombre):   
    try:
        obj_cat_id = ObjectId(cat_id_str)
    except Exception as e:
        print(f"Error al convertir ID: {e}")
        return False

    # si nuevo nombre ya existe en otra categoría
    if categories_col.find_one({"name": nuevo_nombre, "_id": {"$ne": obj_cat_id}}):
        print("Error: Ya existe otra categoría con ese nombre.")
        return False

    filtro = {"_id": obj_cat_id}
    actualizacion = {"$set": {"name": nuevo_nombre}}
    
    try:
        result = categories_col.update_one(filtro, actualizacion)
        # Si encontró el documento o modifivo
        if result.modified_count == 1 or result.matched_count == 1:
            return True
        else:
            return False # No la encontró
    except Exception as e:
        print(f"Error al editar categoría: {e}")
        return False

def editar_tag(tag_id_str, nuevo_nombre):  
    try:
        obj_tag_id = ObjectId(tag_id_str)
    except Exception as e:
        print(f"Error al convertir ID: {e}")
        return False

    if tags_col.find_one({"name": nuevo_nombre, "_id": {"$ne": obj_tag_id}}):
        print("Error: Ya existe otro tag con ese nombre.")
        return False

    filtro = {"_id": obj_tag_id}
    actualizacion = {"$set": {"name": nuevo_nombre}}
    
    try:
        result = tags_col.update_one(filtro, actualizacion)
        if result.modified_count == 1 or result.matched_count == 1:
            return True
        else:
            return False # No lo encontró
    except Exception as e:
        print(f"Error al editar tag: {e}")
        return False

#Eliminar / Delete
def eliminar_usuario(user_id_str):
    """
    Elimina un usuario y sus relaciones como :
    2. Sus artículos.
    3. Comentarios HECHOS por él.
    """
    # 1. ID del usuario
    try:
        obj_user_id = ObjectId(user_id_str)
    except Exception as e:
        print(f"Error al convertir ID de usuario: {e}")
        return False 

    try:
        #Buscar id
        # guardar los IDs de sus artículos para borrar sus comentarios
        articulos_del_usuario_cursor = articles_col.find({"user_id": obj_user_id}, {"_id": 1})
        lista_ids_articulos = [articulo['_id'] for articulo in articulos_del_usuario_cursor]

        if lista_ids_articulos:
            # Borrar  los comentarios de esos artículos de el mismo
            print(f"Borrando comentarios de {len(lista_ids_articulos)} artículos...")
            comments_col.delete_many({"article_id": {"$in": lista_ids_articulos}})
        
        # Borrar todos los artículos del usuario
        print(f"Borrando artículos del usuario {user_id_str}...")
        articles_col.delete_many({"user_id": obj_user_id})
        
        # Borrar todos los comentarios que el usuario escribió (en otros blgs)
        print(f"Borrando comentarios hechos por {user_id_str}...")
        comments_col.delete_many({"user_id": obj_user_id})

        # Borrar al usuario
        print(f"Borrando al usuario {user_id_str}...")
        result = users_col.delete_one({"_id": obj_user_id})
        
        # 6. Verificamos si se borró
        if result.deleted_count == 1:
            return True
        else:
            return False # No encontró al usuario

    except Exception as e:
        print(f"Error durante el borrado en cascada: {e}")
        return False

def eliminar_articulo(article_id_str):
    #Elimina un artículo y TODOS sus comentarios asociados.

    try:
        obj_article_id = ObjectId(article_id_str)
    except Exception as e:
        print(f"Error al convertir ID de artículo: {e}")
        return False

    # Antes de borrar el artículo, se borran todos los comentatios
    try:
        comments_col.delete_many({"article_id": obj_article_id})
    except Exception as e:
        print(f" {e}")
    #Borrar art 
    result = articles_col.delete_one({"_id": obj_article_id})
    
    # 4. Verificamos si se borró
    if result.deleted_count == 1:
        return True
    else:
        return False

def eliminar_comentario_individual(comment_id_str):
    try:
        obj_comment_id = ObjectId(comment_id_str)
    except Exception as e:
        print(f"Error al convertir ID de comentario: {e}")
        return False
    
    try:
        result = comments_col.delete_one({"_id": obj_comment_id})
        return result.deleted_count == 1
    except Exception as e:
        print(f"Error al eliminar comentario: {e}")
        return False

def eliminar_categoria(cat_id_str):
    #Elimina una categoría Y la quita de todos los artículos
    
    try:
        obj_cat_id = ObjectId(cat_id_str)
    except Exception as e:
        print(f"Error al convertir ID: {e}")
        return False
        
    try:
        # $pull actualiza y le quita elemento al array 'categories'
        print(f"Quitando categoría {cat_id_str} de todos los artículos")
        articles_col.update_many(
            {"categories": obj_cat_id}, # Busca artículos que la tengan
            {"$pull": {"categories": obj_cat_id}} 
        )
        
        #  borrar la categoría 
        print(f"Borrando categoría {cat_id_str}...")
        result = categories_col.delete_one({"_id": obj_cat_id})
        
        return result.deleted_count == 1
        
    except Exception as e:
        print(f"Error al eliminar categoría: {e}")
        return False
    
def eliminar_tag(tag_id_str):
    #Elimina un tag Y lo quita de todos los artículos
    
    try:
        obj_tag_id = ObjectId(tag_id_str)
    except Exception as e:
        print(f"Error al convertir ID: {e}")
        return False
        
    try:
        #
        print(f"Quitando tag {tag_id_str} de todos los artículos...")
        articles_col.update_many(
            {"tags": obj_tag_id}, # Busca artículos que lo tengan
            {"$pull": {"tags": obj_tag_id}} 
        )
        
        # borrar el tag
        print(f"Borrando tag {tag_id_str}...")
        result = tags_col.delete_one({"_id": obj_tag_id})
        
        return result.deleted_count == 1
        
    except Exception as e:
        print(f"Error al eliminar tag: {e}")
        return False























