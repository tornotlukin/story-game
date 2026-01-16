## shader_weather.rpy - Rain and snow weather effects
##
## Procedural weather effects that overlay on images. Creates animated
## rain drops or snow particles with configurable speed, angle, and density.
##
## Shaders:
##   - shader.weather_rain - Falling rain streaks
##   - shader.weather_snow - Falling snow particles
##   - shader.weather_overlay - Combined weather with mode selection
##
## @tool-category: Weather
## @tool-description: Rain and snow particle effects

init python:

    # =========================================================================
    # shader.weather_rain - Rain effect
    # =========================================================================

    # @shader: shader.weather_rain
    # @description: Animated rain streaks overlay
    # @animated
    # @param u_speed: float, range=0.5-5.0, default=2.0, description=Rain fall speed
    # @param u_angle: float, range=-0.5-0.5, default=0.1, description=Wind angle (negative=left, positive=right)
    # @param u_density: float, range=0.1-1.0, default=0.5, description=Rain density
    # @param u_length: float, range=0.01-0.1, default=0.04, description=Rain streak length
    # @param u_thickness: float, range=0.001-0.01, default=0.003, description=Rain streak thickness
    # @param u_color: color, default=#AACCFF, description=Rain color
    # @param u_opacity: float, range=0.1-1.0, default=0.6, description=Rain opacity
    renpy.register_shader("shader.weather_rain", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_angle;
        uniform float u_density;
        uniform float u_length;
        uniform float u_thickness;
        uniform vec3 u_color;
        uniform float u_opacity;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        float weather_hash(vec2 p) {
            return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
        }

        vec2 weather_hash2(vec2 p) {
            return vec2(
                fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453),
                fract(sin(dot(p, vec2(269.5, 183.3))) * 43758.5453)
            );
        }
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        // Wrap time to avoid precision issues
        float time = mod(u_time * u_speed, 1000.0);

        // Rain direction vector
        vec2 rainDir = normalize(vec2(u_angle, -1.0));

        // Grid for rain drops
        float gridSize = 0.05 / max(0.1, u_density);
        vec2 uv = v_tex_coord;

        float rain = 0.0;

        // Multiple layers for depth
        for (int layer = 0; layer < 3; layer++) {
            float layerOffset = float(layer) * 0.37;
            float layerSpeed = 1.0 - float(layer) * 0.2;
            float layerSize = 1.0 - float(layer) * 0.3;

            // Offset UV by time and direction
            vec2 movingUV = uv;
            movingUV.y += time * layerSpeed;
            movingUV.x += time * u_angle * layerSpeed;
            movingUV += layerOffset;

            // Grid cell
            vec2 cell = floor(movingUV / gridSize);
            vec2 cellUV = fract(movingUV / gridSize);

            // Random values for this cell
            vec2 randVal = weather_hash2(cell);

            // Only some cells have rain drops
            if (randVal.x < u_density) {
                // Drop position within cell
                vec2 dropPos = vec2(randVal.y, 0.5);

                // Distance to rain streak (line segment)
                vec2 toPoint = cellUV - dropPos;

                // Project onto rain direction
                float alongRain = dot(toPoint, -rainDir);
                vec2 projected = -rainDir * alongRain;
                vec2 perpendicular = toPoint - projected;

                // Check if within streak bounds
                float perpDist = length(perpendicular);
                float streakLen = u_length * layerSize / gridSize;

                if (alongRain > 0.0 && alongRain < streakLen && perpDist < u_thickness / gridSize) {
                    // Fade along streak
                    float fade = 1.0 - alongRain / streakLen;
                    rain = max(rain, fade * layerSize);
                }
            }
        }

        // Blend rain with original
        vec3 result = mix(origColor.rgb, u_color, rain * u_opacity);

        gl_FragColor = vec4(result, origColor.a);
    """)

    # =========================================================================
    # shader.weather_snow - Snow effect
    # =========================================================================

    # @shader: shader.weather_snow
    # @description: Animated falling snow particles
    # @animated
    # @param u_speed: float, range=0.1-2.0, default=0.5, description=Snow fall speed
    # @param u_wind: float, range=-0.5-0.5, default=0.05, description=Wind direction and strength
    # @param u_density: float, range=0.1-1.0, default=0.4, description=Snow density
    # @param u_size: float, range=0.005-0.03, default=0.012, description=Snowflake size
    # @param u_wobble: float, range=0.0-1.0, default=0.3, description=Horizontal drift amount
    # @param u_color: color, default=#FFFFFF, description=Snow color
    # @param u_opacity: float, range=0.3-1.0, default=0.8, description=Snow opacity
    renpy.register_shader("shader.weather_snow", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_speed;
        uniform float u_wind;
        uniform float u_density;
        uniform float u_size;
        uniform float u_wobble;
        uniform vec3 u_color;
        uniform float u_opacity;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        float snow_hash(vec2 p) {
            return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
        }

        vec2 snow_hash2(vec2 p) {
            return vec2(
                fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453),
                fract(sin(dot(p, vec2(269.5, 183.3))) * 43758.5453)
            );
        }
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        float time = mod(u_time * u_speed, 1000.0);

        float gridSize = 0.08 / max(0.1, u_density);
        vec2 uv = v_tex_coord;

        // Aspect ratio correction
        float aspect = u_model_size.x / u_model_size.y;

        float snow = 0.0;

        // Multiple layers for depth
        for (int layer = 0; layer < 4; layer++) {
            float layerOffset = float(layer) * 0.41;
            float layerSpeed = 1.0 - float(layer) * 0.15;
            float layerSizeMod = 1.0 - float(layer) * 0.2;

            // Moving UV
            vec2 movingUV = uv;
            movingUV.y += time * layerSpeed;
            movingUV.x += time * u_wind * layerSpeed;
            movingUV += layerOffset;

            // Grid cell
            vec2 cell = floor(movingUV / gridSize);
            vec2 cellUV = fract(movingUV / gridSize);

            // Random values
            vec2 randVal = snow_hash2(cell);
            float randPhase = snow_hash(cell + 0.5);

            // Only some cells have snowflakes
            if (randVal.x < u_density) {
                // Snowflake position with wobble
                float wobbleX = sin(time * 3.0 + randPhase * 6.28) * u_wobble * 0.3;
                vec2 flakePos = vec2(randVal.y + wobbleX, 0.5);

                // Distance to flake center
                vec2 toFlake = cellUV - flakePos;
                toFlake.x *= aspect; // Correct for aspect ratio

                float dist = length(toFlake);
                float flakeSize = u_size * layerSizeMod / gridSize;

                // Soft circular flake
                if (dist < flakeSize) {
                    float falloff = 1.0 - dist / flakeSize;
                    falloff = falloff * falloff; // Softer edges
                    snow = max(snow, falloff * layerSizeMod);
                }
            }
        }

        // Blend snow with original
        vec3 result = mix(origColor.rgb, u_color, snow * u_opacity);

        gl_FragColor = vec4(result, origColor.a);
    """)

    # =========================================================================
    # shader.weather_overlay - Combined weather with mode selection
    # =========================================================================

    # @shader: shader.weather_overlay
    # @description: Weather effect with rain/snow mode toggle
    # @animated
    # @param u_mode: float, range=0.0-1.0, default=0.0, description=Weather mode (0 = rain, 1 = snow)
    # @param u_speed: float, range=0.2-4.0, default=1.5, description=Fall speed
    # @param u_angle: float, range=-0.5-0.5, default=0.1, description=Wind angle/direction
    # @param u_density: float, range=0.1-1.0, default=0.5, description=Particle density
    # @param u_size: float, range=0.005-0.05, default=0.02, description=Particle size
    # @param u_color: color, default=#FFFFFF, description=Particle color
    # @param u_opacity: float, range=0.2-1.0, default=0.7, description=Effect opacity
    renpy.register_shader("shader.weather_overlay", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_model_size;
        uniform float u_time;
        uniform float u_mode;
        uniform float u_speed;
        uniform float u_angle;
        uniform float u_density;
        uniform float u_size;
        uniform vec3 u_color;
        uniform float u_opacity;
        attribute vec2 a_tex_coord;
        varying vec2 v_tex_coord;
    """, vertex_300="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        float overlay_hash(vec2 p) {
            return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
        }

        vec2 overlay_hash2(vec2 p) {
            return vec2(
                fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453),
                fract(sin(dot(p, vec2(269.5, 183.3))) * 43758.5453)
            );
        }
    """, fragment_300="""
        vec4 origColor = texture2D(tex0, v_tex_coord);

        float time = mod(u_time * u_speed, 1000.0);
        float gridSize = 0.06 / max(0.1, u_density);
        vec2 uv = v_tex_coord;
        float aspect = u_model_size.x / u_model_size.y;

        float effect = 0.0;
        bool isSnow = u_mode > 0.5;

        // Fall direction
        vec2 fallDir = normalize(vec2(u_angle, -1.0));

        for (int layer = 0; layer < 3; layer++) {
            float layerOffset = float(layer) * 0.37;
            float layerSpeed = 1.0 - float(layer) * 0.2;
            float layerSizeMod = 1.0 - float(layer) * 0.25;

            vec2 movingUV = uv;
            movingUV.y += time * layerSpeed;
            movingUV.x += time * u_angle * layerSpeed;
            movingUV += layerOffset;

            vec2 cell = floor(movingUV / gridSize);
            vec2 cellUV = fract(movingUV / gridSize);

            vec2 randVal = overlay_hash2(cell);
            float randPhase = overlay_hash(cell + 0.5);

            if (randVal.x < u_density) {
                vec2 particlePos;

                if (isSnow) {
                    // Snow: wobble horizontally
                    float wobble = sin(time * 2.0 + randPhase * 6.28) * 0.2;
                    particlePos = vec2(randVal.y + wobble, 0.5);
                } else {
                    // Rain: fixed position
                    particlePos = vec2(randVal.y, 0.5);
                }

                vec2 toParticle = cellUV - particlePos;

                if (isSnow) {
                    // Snow: circular soft particle
                    toParticle.x *= aspect;
                    float dist = length(toParticle);
                    float pSize = u_size * layerSizeMod / gridSize;

                    if (dist < pSize) {
                        float falloff = 1.0 - dist / pSize;
                        falloff *= falloff;
                        effect = max(effect, falloff * layerSizeMod);
                    }
                } else {
                    // Rain: elongated streak
                    float alongFall = dot(toParticle, -fallDir);
                    vec2 perpVec = toParticle - (-fallDir * alongFall);
                    float perpDist = length(perpVec);

                    float streakLen = u_size * 2.0 * layerSizeMod / gridSize;
                    float streakThick = u_size * 0.15 / gridSize;

                    if (alongFall > 0.0 && alongFall < streakLen && perpDist < streakThick) {
                        float fade = 1.0 - alongFall / streakLen;
                        effect = max(effect, fade * layerSizeMod);
                    }
                }
            }
        }

        vec3 result = mix(origColor.rgb, u_color, effect * u_opacity);
        gl_FragColor = vec4(result, origColor.a);
    """)
