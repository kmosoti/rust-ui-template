plugins {
    `kotlin-dsl`
}

gradlePlugin {
    plugins {
        create("pluginsForCoolKids") {
            id = "rust"
            implementationClass = "RustPlugin"
        }
    }
}

repositories {
    google {
            content {
                includeGroupByRegex("com[.]android.*")
                includeGroupByRegex("androidx[.].*")
                includeGroupByRegex("com[.]google[.]android.*")
                includeGroupByRegex("com[.]google[.]testing[.]platform.*")
            }
        }
    mavenCentral()
}

dependencies {
    compileOnly(gradleApi())
    implementation("com.android.tools.build:gradle:9.3.1")
}


dependencyLocking { lockAllConfigurations() }
